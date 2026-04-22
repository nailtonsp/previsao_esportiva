import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import poisson
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import inject_custom_css, get_bandeira_url
from utils.data_loader import carregar_dados, carregar_dados_elo, preparar_estruturas
from utils.simulation import simular_jogo, calcular_probabilidades_partida, calcular_lambdas_poisson
from utils.config import MEDIA_GOLS_COPA

inject_custom_css()

st.markdown("## ⚔️ Simulador de Partida Individual")
st.markdown("""
<p style="color: #8a8a9a; font-size: 1rem; margin-bottom: 1.5rem;">
    Selecione duas equipes para simular um confronto direto e ver as probabilidades de cada resultado usando a <b style="color: #00ff88;">distribuição de Poisson</b>.
</p>
""", unsafe_allow_html=True)

# Carregar dados
try:
    df_dados = carregar_dados()
    df_elo = carregar_dados_elo()
    selecoes, elo_dict, grupos_dict, bandeiras_dict, stats_gols_dict = preparar_estruturas(df_dados, df_elo)
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

# Seleção das equipes
col_sel1, col_vs, col_sel2 = st.columns([2, 1, 2])

selecoes_ordenadas = sorted(selecoes)

with col_sel1:
    st.markdown("#### 🏠 Time da Casa")
    time1 = st.selectbox("Selecione o time 1", selecoes_ordenadas, index=selecoes_ordenadas.index("Brasil") if "Brasil" in selecoes_ordenadas else 0, key="time1_select")
    if time1:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <img src="{get_bandeira_url(time1, bandeiras_dict)}" style="width: 100px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,255,136,0.3);">
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: white; margin-top: 0.5rem;">{time1}</div>
            <div style="color: #00ff88; font-size: 1.1rem;">Elo: {elo_dict.get(time1, 1500):.0f}</div>
        </div>
        """, unsafe_allow_html=True)

with col_vs:
    st.markdown("<div style='text-align: center; padding-top: 4rem;'><span style='font-family: Bebas Neue, sans-serif; font-size: 3rem; color: #ff00ff;'>VS</span></div>", unsafe_allow_html=True)

with col_sel2:
    st.markdown("#### 🏃 Time Visitante")
    time2 = st.selectbox("Selecione o time 2", selecoes_ordenadas, index=selecoes_ordenadas.index("Argentina") if "Argentina" in selecoes_ordenadas else 1, key="time2_select")
    if time2:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <img src="{get_bandeira_url(time2, bandeiras_dict)}" style="width: 100px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,204,255,0.3);">
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: white; margin-top: 0.5rem;">{time2}</div>
            <div style="color: #00ccff; font-size: 1.1rem;">Elo: {elo_dict.get(time2, 1500):.0f}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

if time1 and time2 and time1 != time2:
    elo1 = elo_dict.get(time1, 1500)
    elo2 = elo_dict.get(time2, 1500)
    
    prob_matrix, lambda_1, lambda_2, prob_v1, prob_emp, prob_v2 = calcular_probabilidades_partida(
        elo1, elo2, media_gols=MEDIA_GOLS_COPA, k_scale=400, usar_dixon_coles=False
    )
    
    # Métricas de expectativa
    st.markdown("### 📊 Análise do Confronto")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color: #00ff88;">{lambda_1:.2f}</div>
            <div class="stat-label">Gols Esperados {time1}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color: #00ccff;">{lambda_2:.2f}</div>
            <div class="stat-label">Gols Esperados {time2}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color: #ffd700;">{lambda_1 + lambda_2:.2f}</div>
            <div class="stat-label">Total de Gols Esperado</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m4:
        diff_elo = elo1 - elo2
        cor_diff = '#00ff88' if diff_elo > 0 else ('#ff6b6b' if diff_elo < 0 else '#ffd700')
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color: {cor_diff};">{diff_elo:+.0f}</div>
            <div class="stat-label">Diferença Elo</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Probabilidades de Resultado
    st.markdown("### 🎯 Probabilidades de Resultado")
    
    col_prob1, col_prob2, col_prob3 = st.columns(3)
    
    with col_prob1:
        cor_borda1 = '#00ff88' if prob_v1 > prob_v2 and prob_v1 > prob_emp else '#2a2a3a'
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 3px solid {cor_borda1}; border-radius: 16px; padding: 2rem; text-align: center;">
            <img src="{get_bandeira_url(time1, bandeiras_dict)}" style="width: 60px; border-radius: 6px;">
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 3rem; color: #00ff88; margin: 0.5rem 0;">{prob_v1*100:.1f}%</div>
            <div style="color: #8a8a9a; font-size: 1rem;">Vitória {time1}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_prob2:
        cor_borda_emp = '#ffd700' if prob_emp > prob_v1 and prob_emp > prob_v2 else '#2a2a3a'
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 3px solid {cor_borda_emp}; border-radius: 16px; padding: 2rem; text-align: center;">
            <div style="font-size: 2.5rem;">🤝</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 3rem; color: #ffd700; margin: 0.5rem 0;">{prob_emp*100:.1f}%</div>
            <div style="color: #8a8a9a; font-size: 1rem;">Empate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_prob3:
        cor_borda2 = '#00ccff' if prob_v2 > prob_v1 and prob_v2 > prob_emp else '#2a2a3a'
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 3px solid {cor_borda2}; border-radius: 16px; padding: 2rem; text-align: center;">
            <img src="{get_bandeira_url(time2, bandeiras_dict)}" style="width: 60px; border-radius: 6px;">
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 3rem; color: #00ccff; margin: 0.5rem 0;">{prob_v2*100:.1f}%</div>
            <div style="color: #8a8a9a; font-size: 1rem;">Vitória {time2}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Barra de probabilidade
    st.markdown(f"""
    <div style="background: #1a1a2e; border-radius: 20px; height: 40px; display: flex; overflow: hidden; margin: 1rem 0;">
        <div style="width: {prob_v1*100}%; background: linear-gradient(90deg, #00ff88, #00cc6a); display: flex; align-items: center; justify-content: center; color: #0a0a0f; font-weight: bold; font-size: 0.9rem;">
            {prob_v1*100:.0f}%
        </div>
        <div style="width: {prob_emp*100}%; background: linear-gradient(90deg, #ffd700, #ffaa00); display: flex; align-items: center; justify-content: center; color: #0a0a0f; font-weight: bold; font-size: 0.9rem;">
            {prob_emp*100:.0f}%
        </div>
        <div style="width: {prob_v2*100}%; background: linear-gradient(90deg, #00ccff, #0099cc); display: flex; align-items: center; justify-content: center; color: #0a0a0f; font-weight: bold; font-size: 0.9rem;">
            {prob_v2*100:.0f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Heatmap de Placares
    st.markdown("### 🔥 Heatmap de Probabilidade de Placares")
    
    max_gols_display = 6
    prob_display = prob_matrix[:max_gols_display+1, :max_gols_display+1] * 100
    
    placares = []
    for i in range(max_gols_display+1):
        for j in range(max_gols_display+1):
            resultado = "Vitória " + time1 if i > j else ("Empate" if i == j else "Vitória " + time2)
            cor = "#00ff88" if i > j else ("#ffd700" if i == j else "#00ccff")
            placares.append({
                'placar': f"{i} x {j}",
                'prob': prob_matrix[i, j] * 100,
                'resultado': resultado,
                'cor': cor,
                'gols1': i,
                'gols2': j
            })
    
    placares_ordenados = sorted(placares, key=lambda x: x['prob'], reverse=True)
    
    col_heatmap, col_top5 = st.columns([3, 2])
    
    with col_heatmap:
        st.markdown(f"""
        <p style="color: #8a8a9a; font-size: 0.9rem;">
            Linhas = gols de <b style="color: #00ff88;">{time1}</b> | Colunas = gols de <b style="color: #00ccff;">{time2}</b>
        </p>
        """, unsafe_allow_html=True)
        
        annotations_text = [[f"{prob_display[i,j]:.1f}%" for j in range(max_gols_display+1)] for i in range(max_gols_display+1)]
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=prob_display,
            x=[str(i) for i in range(max_gols_display+1)],
            y=[str(i) for i in range(max_gols_display+1)],
            colorscale=[[0, '#0a0a14'], [0.2, '#0d1a33'], [0.4, '#1a3a66'], [0.6, '#2a5a99'], [0.8, '#3a7acc'], [1, '#4a9aff']],
            text=annotations_text,
            texttemplate="%{text}",
            textfont={"size": 14, "color": "white"},
            hovertemplate=f"{time1}: %{{y}} x %{{x}} :{time2}<br>Probabilidade: %{{z:.2f}}%<extra></extra>",
            showscale=True,
             colorbar=dict(
            title=dict(
            text="Prob (%)",
            font=dict(color='#8a8a9a')),
        tickfont=dict(color='#8a8a9a')
    )       ))
        
    fig_heatmap.update_layout(
        xaxis=dict(
            title=dict(
                text=f"Gols {time2}",
                font=dict(color='#00ccff', size=14)
            ),
            tickfont=dict(color='#8a8a9a', size=13)
        ),
        yaxis=dict(
            title=dict(
                text=f"Gols {time1}",
                font=dict(color='#00ccff', size=14)
            ),
            tickfont=dict(color='#8a8a9a', size=13)
        ),
        margin=dict(l=60, r=20, t=30, b=60)
    )       

        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col_top5:
        st.markdown("#### 🏆 Top 5 Placares Mais Prováveis")
        
        for idx, placar in enumerate(placares_ordenados[:5]):
            medalha = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][idx]
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #1e1e2e, #16161f); border-left: 4px solid {placar['cor']}; padding: 1rem 1.2rem; margin: 0.6rem 0; border-radius: 0 12px 12px 0;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 1.5rem;">{medalha}</span>
                        <div>
                            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: white;">{placar['placar']}</div>
                            <div style="color: {placar['cor']}; font-size: 0.85rem;">{placar['resultado']}</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: {placar['cor']};">{placar['prob']:.1f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Over/Under
    st.markdown("### 📈 Probabilidades Over/Under (Total de Gols)")
    
    over_under = {}
    for linha in [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]:
        prob_over = 0
        for i in range(8):
            for j in range(8):
                if i + j > linha:
                    prob_over += prob_matrix[i, j]
        over_under[linha] = prob_over
    
    col_ou1, col_ou2, col_ou3 = st.columns(3)
    linhas_ou = list(over_under.items())
    
    for idx, (linha, prob_over) in enumerate(linhas_ou):
        col = [col_ou1, col_ou2, col_ou3][idx % 3]
        with col:
            prob_under = 1 - prob_over
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #2a2a3a; border-radius: 12px; padding: 1rem; margin: 0.3rem 0; text-align: center;">
                <div style="color: #8a8a9a; font-size: 0.9rem; margin-bottom: 0.5rem;">Linha {linha}</div>
                <div style="display: flex; justify-content: space-around;">
                    <div>
                        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem; color: #00ff88;">Under</div>
                        <div style="font-size: 1.2rem; color: white;">{prob_under*100:.1f}%</div>
                    </div>
                    <div>
                        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem; color: #ff6b6b;">Over</div>
                        <div style="font-size: 1.2rem; color: white;">{prob_over*100:.1f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # BTTS
    st.markdown("### ⚽ Ambas Equipes Marcam (BTTS)")
    
    prob_btts_sim = sum(prob_matrix[i, j] for i in range(8) for j in range(8) if i > 0 and j > 0)
    prob_btts_nao = 1 - prob_btts_sim
    
    col_btts1, col_btts2 = st.columns(2)
    
    with col_btts1:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 2px solid #00ff88; border-radius: 16px; padding: 1.5rem; text-align: center;">
            <div style="font-size: 2rem;">✅</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; color: #00ff88;">{prob_btts_sim*100:.1f}%</div>
            <div style="color: #8a8a9a; font-size: 1rem;">Ambas Marcam - SIM</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_btts2:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 2px solid #ff6b6b; border-radius: 16px; padding: 1.5rem; text-align: center;">
            <div style="font-size: 2rem;">❌</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; color: #ff6b6b;">{prob_btts_nao*100:.1f}%</div>
            <div style="color: #8a8a9a; font-size: 1rem;">Ambas Marcam - NÃO</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Simulação Monte Carlo Rápida
    st.markdown("### 🎲 Simulação Monte Carlo (1000 jogos)")
    
    if st.button("🚀 Simular 1000 Partidas", use_container_width=True, type="primary"):
        resultados_mc = {'v1': 0, 'emp': 0, 'v2': 0, 'gols1': [], 'gols2': [], 'placares': {}}
        sim_config = {'media_gols': MEDIA_GOLS_COPA, 'k_scale': 400, 'usar_dixon_coles': False, 'rho_dixon_coles': -0.13}
        
        progress = st.progress(0)
        
        for i in range(1000):
            *_, ga, gb, _, _, resultado = simular_jogo(elo1, elo2, config=sim_config)
            
            if resultado == 0 or ga > gb:
                resultados_mc['v1'] += 1
            elif resultado == 1 or gb > ga:
                resultados_mc['v2'] += 1
            else:
                resultados_mc['emp'] += 1
            
            resultados_mc['gols1'].append(ga)
            resultados_mc['gols2'].append(gb)
            
            placar_key = f"{ga}x{gb}"
            resultados_mc['placares'][placar_key] = resultados_mc['placares'].get(placar_key, 0) + 1
            
            if (i + 1) % 100 == 0:
                progress.progress((i + 1) / 1000)
        
        progress.progress(1.0)
        st.success("✅ Simulação concluída!")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        
        with col_res1:
            st.metric(f"🏆 Vitórias {time1}", f"{resultados_mc['v1']/10:.1f}%", f"Média gols: {np.mean(resultados_mc['gols1']):.2f}")
        
        with col_res2:
            st.metric("🤝 Empates", f"{resultados_mc['emp']/10:.1f}%", f"Total médio: {np.mean(resultados_mc['gols1']) + np.mean(resultados_mc['gols2']):.2f}")
        
        with col_res3:
            st.metric(f"🏆 Vitórias {time2}", f"{resultados_mc['v2']/10:.1f}%", f"Média gols: {np.mean(resultados_mc['gols2']):.2f}")
        
        st.markdown("#### 📊 Placares mais frequentes:")
        top_placares_mc = sorted(resultados_mc['placares'].items(), key=lambda x: x[1], reverse=True)[:5]
        
        for placar, freq in top_placares_mc:
            st.markdown(f"""
            <div style="background: #1a1a2e; border-radius: 8px; padding: 0.5rem 1rem; margin: 0.2rem 0; display: flex; justify-content: space-between;">
                <span style="color: white; font-size: 1.1rem;">{placar.replace('x', ' x ')}</span>
                <span style="color: #00ff88; font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem;">{freq/10:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)

elif time1 == time2:
    st.warning("⚠️ Por favor, selecione duas equipes diferentes para simular o confronto.")
else:
    st.info("👆 Selecione as duas equipes acima para ver a análise do confronto.")




