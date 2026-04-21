import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import inject_custom_css, get_bandeira_url, get_brasil_style, calcular_entropia, calcular_numero_efetivo_candidatos, calcular_indice_gini
from utils.data_loader import carregar_dados, carregar_dados_elo, preparar_estruturas

inject_custom_css()

st.markdown("## 📊 Resultados da Simulação")

# Carregar dados base
try:
    df_dados = carregar_dados()
    df_elo = carregar_dados_elo()
    selecoes, elo_dict, grupos_dict, bandeiras_dict, stats_gols_dict = preparar_estruturas(df_dados, df_elo)
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

if 'resultado' not in st.session_state or st.session_state.get('resultado') is None:
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: linear-gradient(145deg, #1a1a2e, #12121a); border-radius: 16px; margin: 2rem 0;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🎮</div>
        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: #00ff88; margin-bottom: 0.5rem;">
            Nenhuma simulação executada ainda!
        </div>
        <div style="color: #8a8a9a; font-size: 1.1rem;">
            Vá para a página <b style="color: #00ccff;">Simulação</b> e clique em <b style="color: #00ff88;">INICIAR SIMULAÇÃO</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    df_res = st.session_state['resultado']
    n_sims = st.session_state.get('n_sims', 0)
    tempo = st.session_state.get('tempo', 0)
    finais_contador = st.session_state.get('finais', {})
    config_sim = st.session_state.get('config_simulacao', {})
    
    # Merge com dados das seleções
    df_analise = df_res.copy()
    df_analise['Seleção'] = df_analise.index
    # Verificar colunas disponíveis
    colunas_merge = ['Seleção', 'Grupo']
    for col in ['Confederação', 'Confederacao', 'Melhor_Resultado_Limpo', 'Participacoes_Num']:
        if col in df_dados.columns:
            colunas_merge.append(col)
    df_analise = df_analise.merge(df_dados[colunas_merge], on='Seleção', how='left')
    # Adicionar Elo
    df_analise['Elo'] = df_analise['Seleção'].map(elo_dict)
    df_analise = df_analise.set_index('Seleção')
    
    # ============ FAVORITO ============
    st.markdown("### 🏆 O Grande Favorito")
    
    favorito = df_res.index[0]
    prob_favorito = df_res['Campeão'].iloc[0] * 100
    
    brasil_style_fav = get_brasil_style(favorito, '#ffd700')
    if brasil_style_fav['is_brasil']:
        cor_borda_fav = '#009c3b'
        bg_fav = 'linear-gradient(145deg, #009c3b22, #ffd70015, #009c3b22)'
        glow_fav = 'box-shadow: 0 0 40px rgba(0, 156, 59, 0.5), 0 0 60px rgba(255, 215, 0, 0.3);'
    else:
        cor_borda_fav = '#ffd700'
        bg_fav = 'linear-gradient(145deg, #1a1a2e, #0d0d14)'
        glow_fav = 'box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);'
    
    st.markdown(f"""
    <div style="background: {bg_fav}; border: 3px solid {cor_borda_fav}; border-radius: 20px; padding: 2rem; margin: 1rem 0; text-align: center; {glow_fav}">
        <div style="font-size: 0.9rem; color: {cor_borda_fav}; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 0.5rem;">Maior Probabilidade de Título</div>
        <img src="{get_bandeira_url(favorito, bandeiras_dict)}" style="width: 120px; border-radius: 10px; box-shadow: 0 8px 25px rgba(0,0,0,0.5); margin: 1rem 0;">
        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 3.5rem; color: white; margin: 0.5rem 0;">{favorito}</div>
        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 4rem; color: {cor_borda_fav};">{prob_favorito:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============ TOP 10 ============
    st.markdown("---")
    st.markdown("### 🎯 Top 10 Candidatos ao Título")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        top10 = df_res.head(10)
        for idx, (selecao, row) in enumerate(top10.iterrows()):
            pos = idx + 1
            medalha = "🥇" if pos == 1 else ("🥈" if pos == 2 else ("🥉" if pos == 3 else f"#{pos}"))
            cor = '#ffd700' if pos == 1 else ('#c0c0c0' if pos == 2 else ('#cd7f32' if pos == 3 else '#00ff88'))
            prob = row['Campeão'] * 100
            
            brasil_style = get_brasil_style(selecao, cor)
            bg_cor = brasil_style['borda'] if brasil_style['is_brasil'] else cor
            extra_style = brasil_style['glow'] if brasil_style['is_brasil'] else ''
            cor_texto = '#ffd700' if brasil_style['is_brasil'] else 'white'
            
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, {bg_cor}22, transparent); border-left: 4px solid {bg_cor}; padding: 0.6rem 1rem; margin: 0.3rem 0; border-radius: 0 8px 8px 0; display: flex; justify-content: space-between; align-items: center; {extra_style}">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.2rem; width: 30px;">{medalha}</span>
                    <img src="{get_bandeira_url(selecao, bandeiras_dict)}" style="width: 28px; border-radius: 3px;">
                    <span style="color: {cor_texto}; font-weight: 600;">{selecao}</span>
                </div>
                <span style="color: {bg_cor}; font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem;">{prob:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        top10_rev = df_res.head(10).iloc[::-1]
        fig_top10 = go.Figure()
        fig_top10.add_trace(go.Bar(
            y=top10_rev.index,
            x=top10_rev['Campeão'] * 100,
            orientation='h',
            marker=dict(color=top10_rev['Campeão'] * 100, colorscale=[[0, '#1a1a2e'], [0.3, '#00ccff'], [1, '#00ff88']]),
            text=[f"{v:.1f}%" for v in top10_rev['Campeão'] * 100],
            textposition='outside',
            textfont=dict(color='#00ff88', size=12)
        ))
        fig_top10.update_layout(
            title="Probabilidade de Título (%)",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='#8a8a9a', title_font_color='#00ff88',
            height=450, margin=dict(l=100, r=60)
        )
        st.plotly_chart(fig_top10, use_container_width=True)
    
    # ============ POR CONFEDERAÇÃO ============
    st.markdown("---")
    st.markdown("### 🌍 Probabilidades por Confederação")
    
    # Verificar se coluna Confederação existe
    col_conf = 'Confederação' if 'Confederação' in df_analise.columns else ('Confederacao' if 'Confederacao' in df_analise.columns else None)
    if col_conf is None:
        # Criar coluna baseada no grupo ou usar padrão
        df_analise['Confederação'] = 'N/A'
        col_conf = 'Confederação'
    
    prob_conf = df_analise.groupby(col_conf).agg({'Campeão': 'sum', 'Final': 'sum', 'Semis': 'sum'}).sort_values('Campeão', ascending=False)
    cores_conf = {'UEFA': '#0055a4', 'CONMEBOL': '#009c3b', 'CONCACAF': '#c8102e', 'AFC': '#ff6600', 'CAF': '#ffd700', 'OFC': '#00ccff', 'N/A': '#8a8a9a'}
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        for conf, row in prob_conf.iterrows():
            cor = cores_conf.get(conf, '#8a8a9a')
            prob = row['Campeão'] * 100
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, {cor}33, transparent); border-left: 5px solid {cor}; padding: 1rem 1.2rem; margin: 0.4rem 0; border-radius: 0 10px 10px 0; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: white; font-weight: 600; font-size: 1.1rem;">{conf}</span>
                <span style="color: {cor}; font-family: 'Bebas Neue', sans-serif; font-size: 2rem;">{prob:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        fig_conf = px.pie(
            values=prob_conf['Campeão'].values * 100,
            names=prob_conf.index,
            color=prob_conf.index,
            color_discrete_map=cores_conf,
            hole=0.4
        )
        fig_conf.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='#8a8a9a', showlegend=False, height=300,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_conf, use_container_width=True)
    
    # ============ ÍNDICES DE COMPETITIVIDADE ============
    st.markdown("---")
    st.markdown("### 📊 Índices de Competitividade")
    
    probs_campeao = df_res['Campeão'].values
    entropia = calcular_entropia(probs_campeao)
    num_efetivo = calcular_numero_efetivo_candidatos(probs_campeao)
    gini = calcular_indice_gini(probs_campeao)
    entropia_max = np.log2(len(probs_campeao))
    incerteza_relativa = (entropia / entropia_max) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #00ff88; border-radius: 12px; padding: 1.2rem; text-align: center;">
            <div style="color: #8a8a9a; font-size: 0.8rem; text-transform: uppercase;">Entropia</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; color: #00ff88;">{entropia:.2f}</div>
            <div style="color: #8a8a9a; font-size: 0.75rem;">bits</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #00ccff; border-radius: 12px; padding: 1.2rem; text-align: center;">
            <div style="color: #8a8a9a; font-size: 0.8rem; text-transform: uppercase;">Nº Efetivo Candidatos</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; color: #00ccff;">{num_efetivo:.1f}</div>
            <div style="color: #8a8a9a; font-size: 0.75rem;">de {len(df_res)} seleções</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #ffd700; border-radius: 12px; padding: 1.2rem; text-align: center;">
            <div style="color: #8a8a9a; font-size: 0.8rem; text-transform: uppercase;">Índice Gini</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; color: #ffd700;">{gini:.3f}</div>
            <div style="color: #8a8a9a; font-size: 0.75rem;">concentração</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #ff00ff; border-radius: 12px; padding: 1.2rem; text-align: center;">
            <div style="color: #8a8a9a; font-size: 0.8rem; text-transform: uppercase;">Incerteza Relativa</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; color: #ff00ff;">{incerteza_relativa:.1f}%</div>
            <div style="color: #8a8a9a; font-size: 0.75rem;">do máximo</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============ HEATMAP ============
    st.markdown("---")
    st.markdown("### 🔥 Heatmap - Top 15 Seleções")
    
    top15 = df_res.head(15)
    fig_heat = px.imshow(
        top15.values * 100,
        labels=dict(x="Fase", y="Seleção", color="%"),
        x=top15.columns.tolist(),
        y=top15.index.tolist(),
        color_continuous_scale=[[0, '#0a1628'], [0.25, '#0d2847'], [0.5, '#1a5a9a'], [0.75, '#3a8acc'], [1, '#5abaff']],
        aspect="auto"
    )
    fig_heat.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_color='#8a8a9a', height=500
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    
    # ============ TABELA COMPLETA ============
    st.markdown("---")
    st.markdown("### 📋 Tabela Completa de Resultados")
    
    df_display_res = df_res.copy()
    df_display_res['Ranking'] = range(1, len(df_display_res) + 1)
    df_display_res = df_display_res[['Ranking'] + [col for col in df_display_res.columns if col != 'Ranking']]
    
    for col in df_display_res.columns:
        if col != 'Ranking':
            df_display_res[col] = (df_display_res[col] * 100).round(2).astype(str) + '%'
    
    st.dataframe(df_display_res, use_container_width=True, height=500)
    
    # ============ EXPORTAR ============
    st.markdown("---")
    st.markdown("### 💾 Exportar Resultados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df_res.to_csv()
        st.download_button("📥 Download CSV", csv, f"copa2026_sim_{n_sims}.csv", "text/csv", use_container_width=True)
    
    with col2:
        st.metric("📊 Total de Seleções", f"{len(df_res)}")




