import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import inject_custom_css, get_bandeira_url, get_brasil_style
from utils.data_loader import carregar_dados, carregar_dados_elo, preparar_estruturas
from utils.simulation import (
    simular_uma_copa, calcular_lambdas_poisson, calcular_probabilidades_partida,
    calcular_lambdas_poisson_dinamico, calcular_probabilidades_partida_dinamico,
    calcular_media_dinamica, elo_to_forca, calcular_razao_forca, 
    ELO_SCALE_DEFAULT, FATOR_AMORTECIMENTO
)

inject_custom_css()

st.markdown("## 🎮 Simulação Monte Carlo")

# Carregar dados
try:
    df_dados = carregar_dados()
    df_elo = carregar_dados_elo()
    selecoes, elo_dict, grupos_dict, bandeiras_dict, stats_gols_dict = preparar_estruturas(df_dados, df_elo)
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

# ============ INPUTS GLOBAIS (TOPO) ============
st.markdown("### ⚙️ Parâmetros do Modelo Elo-Poisson")

col_param1, col_param2, col_param3, col_param4, col_param5 = st.columns([1, 1, 1, 1, 1.5])

with col_param1:
    modo_gols = st.radio("📊 Média de Gols", ["Estático", "Dinâmico"], 
                          help="Estático: usa m fixo | Dinâmico: calcula m baseado em GF/GS")

with col_param2:
    if modo_gols == "Estático":
        media_gols = st.number_input("⚽ **m**", min_value=2.0, max_value=4.0, value=2.75, step=0.05,
                                      help="Média fixa de gols por partida")
    else:
        media_gols = st.number_input("⚽ **m base**", min_value=2.0, max_value=4.0, value=2.75, step=0.05,
                                      help="Média base da liga (referência)")

with col_param3:
    k_scale = st.number_input("📊 **K**", min_value=100, max_value=3000, value=400, step=100,
                               help="Escala Elo: K pts = 10x força")

with col_param4:
    usar_dixon_coles = st.checkbox("🔧 Dixon-Coles", value=False, help="↑ empates")
    if usar_dixon_coles:
        rho_dixon = st.slider("ρ", min_value=-0.25, max_value=0.0, value=-0.13, step=0.01)
    else:
        rho_dixon = -0.13

with col_param5:
    with st.expander("📖 Metodologia", expanded=False):
        if modo_gols == "Estático":
            st.markdown(f"""
            **Modo Estático** (m = {media_gols})
            
            1. f = 10^(Elo/K)
            2. m₁ = m × f₁/(f₁+f₂)
            3. Gols ~ Poisson(m)
            """)
        else:
            st.markdown(f"""
            **Modo Dinâmico**
            
            1. Calcula forças de Atq/Def
            2. m = Atq₁×Def₂ + Atq₂×Def₁
            3. Usa Elo para distribuir m
            
            *Jogos defensivos → m baixo*
            *Jogos ofensivos → m alto*
            """)

st.markdown("---")

# ============ DUAS COLUNAS: LABORATÓRIO E HEATMAP ============
col_lab, col_heat = st.columns([1, 1])

# ============ COLUNA ESQUERDA: LABORATÓRIO ============
with col_lab:
    st.markdown("### 🧪 Laboratório Elo-Poisson")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        selecao_lab1 = st.selectbox("Seleção 1", sorted(selecoes), 
                                     index=sorted(selecoes).index("Brasil") if "Brasil" in selecoes else 0,
                                     key="lab_sel1")
        elo1 = elo_dict.get(selecao_lab1, 1500)
        stats1 = stats_gols_dict.get(selecao_lab1, (1.375, 1.375))
    
    with col_s2:
        selecao_lab2 = st.selectbox("Seleção 2", sorted(selecoes), 
                                     index=sorted(selecoes).index("Argentina") if "Argentina" in selecoes else 1,
                                     key="lab_sel2")
        elo2 = elo_dict.get(selecao_lab2, 1500)
        stats2 = stats_gols_dict.get(selecao_lab2, (1.375, 1.375))
    
    # Calcular forças e lambdas
    razao = calcular_razao_forca(elo1, elo2, k_scale)
    
    if modo_gols == "Dinâmico":
        m1_lab, m2_lab, m_total = calcular_lambdas_poisson_dinamico(
            elo1, elo2, stats1, stats2, k_scale, media_gols, FATOR_AMORTECIMENTO
        )
    else:
        m1_lab, m2_lab = calcular_lambdas_poisson(elo1, elo2, media_gols, k_scale)
        m_total = media_gols
    
    # Mostrar estatísticas de GF/GS se modo dinâmico
    if modo_gols == "Dinâmico":
        st.markdown(f"""
        <div style="display: flex; gap: 8px; margin: 0.3rem 0;">
            <div style="flex: 1; background: #12121a; border-radius: 6px; padding: 0.4rem; text-align: center;">
                <div style="color: #00ff88; font-size: 0.7rem;">GF: {stats1[0]:.2f} | GS: {stats1[1]:.2f}</div>
            </div>
            <div style="flex: 1; background: #12121a; border-radius: 6px; padding: 0.4rem; text-align: center;">
                <div style="color: #ffd700; font-size: 0.75rem; font-weight: bold;">m = {m_total:.2f}</div>
            </div>
            <div style="flex: 1; background: #12121a; border-radius: 6px; padding: 0.4rem; text-align: center;">
                <div style="color: #00ccff; font-size: 0.7rem;">GF: {stats2[0]:.2f} | GS: {stats2[1]:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Elo e Lambda
    st.markdown(f"""
    <div style="display: flex; gap: 8px; margin: 0.5rem 0;">
        <div style="flex: 1; background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #00ff88; border-radius: 8px; padding: 0.5rem; text-align: center;">
            <div style="color: #8a8a9a; font-size: 0.65rem;">Elo: {elo1:.0f}</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.3rem; color: #00ff88;">λ₁ = {m1_lab:.2f}</div>
        </div>
        <div style="flex: 0.8; background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #ffd700; border-radius: 8px; padding: 0.5rem; text-align: center;">
            <div style="color: #8a8a9a; font-size: 0.65rem;">Razão</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.3rem; color: #ffd700;">{razao:.1f}x</div>
        </div>
        <div style="flex: 1; background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #00ccff; border-radius: 8px; padding: 0.5rem; text-align: center;">
            <div style="color: #8a8a9a; font-size: 0.65rem;">Elo: {elo2:.0f}</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.3rem; color: #00ccff;">λ₂ = {m2_lab:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Probabilidades
    if modo_gols == "Dinâmico":
        prob_matrix, _, _, prob_v1, prob_emp, prob_v2, _ = calcular_probabilidades_partida_dinamico(
            elo1, elo2, stats1, stats2, k_scale, media_gols, FATOR_AMORTECIMENTO,
            usar_dixon_coles=usar_dixon_coles, rho=rho_dixon
        )
    else:
        prob_matrix, _, _, prob_v1, prob_emp, prob_v2 = calcular_probabilidades_partida(
            elo1, elo2, media_gols, k_scale, usar_dixon_coles=usar_dixon_coles, rho=rho_dixon
        )
    
    # Cards de probabilidade
    st.markdown(f"""
    <div style="display: flex; gap: 6px; margin: 0.6rem 0;">
        <div style="flex: 1; background: linear-gradient(145deg, #1a1a2e, #12121a); border: 2px solid {'#00ff88' if prob_v1 > max(prob_emp, prob_v2) else '#2a2a3a'}; border-radius: 10px; padding: 0.6rem; text-align: center;">
            <img src="{get_bandeira_url(selecao_lab1, bandeiras_dict)}" style="width: 28px; border-radius: 3px;">
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: #00ff88;">{prob_v1*100:.1f}%</div>
        </div>
        <div style="flex: 1; background: linear-gradient(145deg, #1a1a2e, #12121a); border: 2px solid {'#ffd700' if prob_emp > max(prob_v1, prob_v2) else '#2a2a3a'}; border-radius: 10px; padding: 0.6rem; text-align: center;">
            <div style="font-size: 1.2rem;">🤝</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: #ffd700;">{prob_emp*100:.1f}%</div>
        </div>
        <div style="flex: 1; background: linear-gradient(145deg, #1a1a2e, #12121a); border: 2px solid {'#00ccff' if prob_v2 > max(prob_v1, prob_emp) else '#2a2a3a'}; border-radius: 10px; padding: 0.6rem; text-align: center;">
            <img src="{get_bandeira_url(selecao_lab2, bandeiras_dict)}" style="width: 28px; border-radius: 3px;">
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: #00ccff;">{prob_v2*100:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Barra de probabilidade
    st.markdown(f"""
    <div style="background: #1a1a2e; border-radius: 12px; height: 22px; display: flex; overflow: hidden; margin: 0.4rem 0;">
        <div style="width: {prob_v1*100}%; background: linear-gradient(90deg, #00ff88, #00cc6a); display: flex; align-items: center; justify-content: center; color: #0a0a0f; font-weight: bold; font-size: 0.65rem;">{prob_v1*100:.0f}%</div>
        <div style="width: {prob_emp*100}%; background: linear-gradient(90deg, #ffd700, #ffaa00); display: flex; align-items: center; justify-content: center; color: #0a0a0f; font-weight: bold; font-size: 0.65rem;">{prob_emp*100:.0f}%</div>
        <div style="width: {prob_v2*100}%; background: linear-gradient(90deg, #00ccff, #0099cc); display: flex; align-items: center; justify-content: center; color: #0a0a0f; font-weight: bold; font-size: 0.65rem;">{prob_v2*100:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

# ============ COLUNA DIREITA: HEATMAP ============
with col_heat:
    st.markdown("### 🔥 Heatmap de Placares")
    
    max_gols_display = 6
    prob_display = prob_matrix[:max_gols_display+1, :max_gols_display+1] * 100
    
    annotations_text = [[f"{prob_display[i,j]:.1f}%" for j in range(max_gols_display+1)] for i in range(max_gols_display+1)]
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=prob_display,
        x=[str(i) for i in range(max_gols_display+1)],
        y=[str(i) for i in range(max_gols_display+1)],
        colorscale=[[0, '#0a0a14'], [0.2, '#0d1a33'], [0.4, '#1a3a66'], [0.6, '#2a5a99'], [0.8, '#3a7acc'], [1, '#4a9aff']],
        text=annotations_text,
        texttemplate="%{text}",
        textfont={"size": 11, "color": "white"},
        hovertemplate=f"{selecao_lab1}: %{{y}} x %{{x}} :{selecao_lab2}<br>Prob: %{{z:.2f}}%<extra></extra>",
        showscale=False
    ))
    
    fig_heatmap.update_layout(
        xaxis=dict(
            title=dict(
                text=f"Gols {selecao_lab2}",
                font=dict(color='#00ccff', size=12)
            ),
            tickfont=dict(color='#8a8a9a', size=11)
        )
    ) 

    st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# ============ SIMULAÇÃO DA COPA (SEM COLUNAS) ============
st.markdown("### 🏆 Simulação da Copa 2026")

col_sim1, col_sim2, col_sim3 = st.columns([2, 1, 1])

with col_sim1:
    n_simulacoes = st.slider("🔢 Número de Simulações", min_value=100, max_value=100000, value=10000, step=100)

with col_sim2:
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #ffd700; border-radius: 8px; padding: 0.8rem; text-align: center; margin-top: 0.5rem;">
        <div style="color: #8a8a9a; font-size: 0.7rem;">Modo</div>
        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem; color: #ffd700;">{modo_gols}</div>
    </div>
    """, unsafe_allow_html=True)

with col_sim3:
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #00ff88; border-radius: 8px; padding: 0.8rem; text-align: center; margin-top: 0.5rem;">
        <div style="color: #8a8a9a; font-size: 0.7rem;">Config</div>
        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1rem; color: #00ff88;">K={k_scale} | m={media_gols}</div>
    </div>
    """, unsafe_allow_html=True)

iniciar = st.button("🚀 INICIAR SIMULAÇÃO", use_container_width=True, type="primary")

if iniciar:
    sim_config = {
        'media_gols': media_gols,
        'k_scale': k_scale,
        'usar_dixon_coles': usar_dixon_coles,
        'rho_dixon_coles': rho_dixon,
        'modo_dinamico': modo_gols == "Dinâmico",
        'amortecimento': FATOR_AMORTECIMENTO,
    }
    
    # Container para métricas em tempo real
    st.markdown("#### 📊 Monitoramento em Tempo Real")
    
    col_prog1, col_prog2, col_prog3, col_prog4 = st.columns(4)
    with col_prog1:
        metric_progresso = st.empty()
    with col_prog2:
        metric_tempo = st.empty()
    with col_prog3:
        metric_velocidade = st.empty()
    with col_prog4:
        metric_eta = st.empty()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Top 3 em tempo real
    st.markdown("#### 👑 Líderes Parciais")
    col_top1, col_top2, col_top3 = st.columns(3)
    with col_top1:
        top1_container = st.empty()
    with col_top2:
        top2_container = st.empty()
    with col_top3:
        top3_container = st.empty()
    
    idx = {t: i for i, t in enumerate(selecoes)}
    acumulador = np.zeros((len(selecoes), 7), dtype=np.int32)
    
    finais_contador = {}
    semis_contador = {}
    quartas_contador = {}
    
    tempo_inicio = time.time()
    campeoes_parciais = {}
    
    for i in range(n_simulacoes):
        resultado, confrontos = simular_uma_copa(
            selecoes, elo_dict, grupos_dict, sim_config, 
            stats_gols_dict=stats_gols_dict if modo_gols == "Dinâmico" else None
        )
        
        if confrontos['final']:
            finais_contador[confrontos['final']] = finais_contador.get(confrontos['final'], 0) + 1
        if confrontos['semis']:
            semis_contador[confrontos['semis']] = semis_contador.get(confrontos['semis'], 0) + 1
        if confrontos['quartas']:
            quartas_contador[confrontos['quartas']] = quartas_contador.get(confrontos['quartas'], 0) + 1
        
        for time_sel, stats in resultado.items():
            acumulador[idx[time_sel]] += stats
            if stats[6] == 1:
                campeoes_parciais[time_sel] = campeoes_parciais.get(time_sel, 0) + 1
        
        if (i + 1) % 50 == 0 or i == 0:
            progresso = (i + 1) / n_simulacoes
            progress_bar.progress(progresso)
            
            tempo_decorrido = time.time() - tempo_inicio
            vel = (i + 1) / tempo_decorrido if tempo_decorrido > 0 else 0
            tempo_restante = (n_simulacoes - i - 1) / vel if vel > 0 else 0
            
            # Atualizar métricas
            metric_progresso.metric("📈 Progresso", f"{progresso*100:.1f}%")
            metric_tempo.metric("⏱️ Tempo", f"{tempo_decorrido:.1f}s")
            metric_velocidade.metric("⚡ Velocidade", f"{vel:.0f}/s")
            metric_eta.metric("🏁 ETA", f"{tempo_restante:.0f}s")
            
            status_text.markdown(f"**Simulando...** {i + 1:,} / {n_simulacoes:,} copas")
            
            # Atualizar Top 3
            top3 = sorted(campeoes_parciais.items(), key=lambda x: x[1], reverse=True)[:3]
            
            if len(top3) >= 1:
                sel1, cnt1 = top3[0]
                prob1 = cnt1 / (i + 1) * 100
                top1_container.markdown(f"""
                <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 2px solid #ffd700; border-radius: 10px; padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem;">🥇</div>
                    <img src="{get_bandeira_url(sel1, bandeiras_dict)}" style="width: 40px; border-radius: 4px; margin: 0.3rem 0;">
                    <div style="color: white; font-weight: 600;">{sel1}</div>
                    <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: #ffd700;">{prob1:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            if len(top3) >= 2:
                sel2, cnt2 = top3[1]
                prob2 = cnt2 / (i + 1) * 100
                top2_container.markdown(f"""
                <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 2px solid #c0c0c0; border-radius: 10px; padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem;">🥈</div>
                    <img src="{get_bandeira_url(sel2, bandeiras_dict)}" style="width: 40px; border-radius: 4px; margin: 0.3rem 0;">
                    <div style="color: white; font-weight: 600;">{sel2}</div>
                    <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: #c0c0c0;">{prob2:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            if len(top3) >= 3:
                sel3, cnt3 = top3[2]
                prob3 = cnt3 / (i + 1) * 100
                top3_container.markdown(f"""
                <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 2px solid #cd7f32; border-radius: 10px; padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem;">🥉</div>
                    <img src="{get_bandeira_url(sel3, bandeiras_dict)}" style="width: 40px; border-radius: 4px; margin: 0.3rem 0;">
                    <div style="color: white; font-weight: 600;">{sel3}</div>
                    <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: #cd7f32;">{prob3:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
    
    progress_bar.progress(1.0)
    tempo_total = time.time() - tempo_inicio
    
    # Métricas finais
    metric_progresso.metric("📈 Progresso", "100%")
    metric_tempo.metric("⏱️ Tempo Total", f"{tempo_total:.1f}s")
    metric_velocidade.metric("⚡ Média", f"{n_simulacoes/tempo_total:.0f}/s")
    metric_eta.metric("🏁 Status", "✅")
    
    status_text.markdown(f"✅ **CONCLUÍDO!** {n_simulacoes:,} simulações em {tempo_total:.1f}s ({n_simulacoes/tempo_total:.0f}/s)")
    
    colunas = ['Fase Grupos', 'Top 32', 'Oitavas', 'Quartas', 'Semis', 'Final', 'Campeão']
    df_resultado = pd.DataFrame(acumulador / n_simulacoes, index=selecoes, columns=colunas)
    df_resultado = df_resultado.sort_values('Campeão', ascending=False)
    
    # Salvar no session_state
    st.session_state['resultado'] = df_resultado
    st.session_state['n_sims'] = n_simulacoes
    st.session_state['tempo'] = tempo_total
    st.session_state['finais'] = finais_contador
    st.session_state['semis'] = semis_contador
    st.session_state['quartas'] = quartas_contador
    st.session_state['config_simulacao'] = {
        'metodologia': f'Elo-Poisson {"Dinâmico" if modo_gols == "Dinâmico" else "Estático"} (K={k_scale})',
        'modo_gols': modo_gols,
        'dixon_coles': usar_dixon_coles,
        'rho': rho_dixon if usar_dixon_coles else None,
        'media_gols': media_gols,
        'k_scale': k_scale,
    }
    
    st.success("🎉 Simulação finalizada com sucesso!")
    
    st.markdown("---")
    
    # Preview Top 10
    st.markdown("### 🏆 Top 10 Favoritos")
    
    top10 = df_resultado.head(10)
    
    col_rank1, col_rank2 = st.columns(2)
    
    with col_rank1:
        for idx_row, (selecao, row) in enumerate(top10.head(5).iterrows()):
            medalha = "🥇" if idx_row == 0 else ("🥈" if idx_row == 1 else ("🥉" if idx_row == 2 else f"#{idx_row+1}"))
            cor = '#ffd700' if idx_row == 0 else ('#c0c0c0' if idx_row == 1 else ('#cd7f32' if idx_row == 2 else '#00ff88'))
            
            brasil_style = get_brasil_style(selecao, cor)
            if brasil_style['is_brasil']:
                bg_style = brasil_style['bg']
                cor = brasil_style['borda']
                extra_style = brasil_style['glow']
                cor_texto = '#ffd700'
            else:
                bg_style = 'linear-gradient(145deg, #1e1e2e, #16161f)'
                extra_style = ''
                cor_texto = 'white'
            
            elo_sel = elo_dict.get(selecao, 1500)
            st.markdown(f"""
            <div style="background: {bg_style}; border-left: 4px solid {cor}; padding: 0.6rem 0.8rem; margin: 0.2rem 0; border-radius: 0 8px 8px 0; display: flex; align-items: center; justify-content: space-between; {extra_style}">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.2rem;">{medalha}</span>
                    <img src="{get_bandeira_url(selecao, bandeiras_dict)}" style="width: 28px; border-radius: 3px;">
                    <div>
                        <span style="color: {cor_texto}; font-size: 1rem; font-weight: 600;">{selecao}</span>
                        <span style="color: #8a8a9a; font-size: 0.75rem; margin-left: 6px;">(Elo {elo_sel:.0f})</span>
                    </div>
                </div>
                <span style="color: {'#009c3b' if brasil_style['is_brasil'] else '#00ff88'}; font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem;">{row['Campeão']*100:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col_rank2:
        for idx_row, (selecao, row) in enumerate(top10.tail(5).iterrows(), start=5):
            cor = '#00ff88'
            bg_style = 'linear-gradient(145deg, #1e1e2e, #16161f)'
            
            brasil_style = get_brasil_style(selecao, cor)
            if brasil_style['is_brasil']:
                bg_style = brasil_style['bg']
                cor = brasil_style['borda']
                extra_style = brasil_style['glow']
                cor_texto = '#ffd700'
            else:
                extra_style = ''
                cor_texto = 'white'
            
            elo_sel = elo_dict.get(selecao, 1500)
            st.markdown(f"""
            <div style="background: {bg_style}; border-left: 4px solid {cor}; padding: 0.6rem 0.8rem; margin: 0.2rem 0; border-radius: 0 8px 8px 0; display: flex; align-items: center; justify-content: space-between; {extra_style}">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1rem; color: #8a8a9a;">#{idx_row+1}</span>
                    <img src="{get_bandeira_url(selecao, bandeiras_dict)}" style="width: 28px; border-radius: 3px;">
                    <div>
                        <span style="color: {cor_texto}; font-size: 1rem; font-weight: 600;">{selecao}</span>
                        <span style="color: #8a8a9a; font-size: 0.75rem; margin-left: 6px;">(Elo {elo_sel:.0f})</span>
                    </div>
                </div>
                <span style="color: {'#009c3b' if brasil_style['is_brasil'] else '#00ff88'}; font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem;">{row['Campeão']*100:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.info("👉 Análises completas e detalhadas em **📊 Resultados**")




