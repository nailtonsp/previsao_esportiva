import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import inject_custom_css, get_bandeira_url, get_bandeira_html
from utils.data_loader import carregar_dados, carregar_dados_elo, preparar_estruturas
from utils.config import (
    CAMINHO_DADOS, CAMINHO_ELO, CAMINHO_HISTORICO, CAMINHO_JOGOS,
    PESO_RANKING_FIFA, PESO_PARTICIPACOES, PESO_MELHOR_RESULTADO, RESULTADO_COPA_PONTOS
)

# Injetar CSS
inject_custom_css()

st.markdown("## 📋 Datasets")

# Carregar dados
try:
    df_dados = carregar_dados()
    df_elo = carregar_dados_elo()
    selecoes, elo_dict, grupos_dict, bandeiras_dict, stats_gols_dict = preparar_estruturas(df_dados, df_elo)
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

# Sub-abas para os diferentes datasets
dataset_tab1, dataset_tab2, dataset_tab3, dataset_tab4 = st.tabs([
    "📊 Seleções Copa 2026", 
    "🏆 Histórico de Copas", 
    "📈 Ranking ELO", 
    "📅 Tabela de Jogos"
])

# ============ SUB-TAB 1: SELEÇÕES COPA 2026 ============
with dataset_tab1:
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid rgba(0, 255, 136, 0.3); border-radius: 12px; padding: 1rem; margin: 1rem 0;">
        <div style="color: #00ff88; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">⚽ 48 Seleções Classificadas para a Copa 2026</div>
        <div style="color: #8a8a9a; font-size: 0.9rem;">
            Dados completos das seleções participantes da Copa do Mundo FIFA 2026 (USA/CAN/MEX).
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas principais
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    with col_e1:
        st.metric("🌍 Seleções", len(df_dados))
    with col_e2:
        st.metric("🏆 Grupos", df_dados['Grupo'].nunique() if 'Grupo' in df_dados.columns else 12)
    with col_e3:
        if 'Valor_Mercado_Milhoes_EUR' in df_dados.columns:
            valor_total = pd.to_numeric(df_dados['Valor_Mercado_Milhoes_EUR'], errors='coerce').sum()
            st.metric("💰 Valor Total", f"€{valor_total:,.0f}M")
        else:
            col_conf_name = 'Confederação' if 'Confederação' in df_dados.columns else ('Confederacao' if 'Confederacao' in df_dados.columns else None)
            st.metric("⭐ Confederações", df_dados[col_conf_name].nunique() if col_conf_name else 6)
    with col_e4:
        if 'Populacao' in df_dados.columns:
            pop_total = pd.to_numeric(df_dados['Populacao'], errors='coerce').sum()
            st.metric("👥 Pop. Total", f"{pop_total/1e9:.2f}B")
        else:
            st.metric("📊 Registros", len(df_dados))
    
    # Visualização dos Grupos com Bandeiras
    st.markdown("### 🏟️ Grupos da Copa 2026")
    grupos_ordenados = sorted(grupos_dict.keys())
    num_grupos = len(grupos_ordenados)
    
    for i in range(0, num_grupos, 6):
        cols = st.columns(6)
        for j, col in enumerate(cols):
            if i + j < num_grupos:
                grupo = grupos_ordenados[i + j]
                times_grupo = grupos_dict[grupo]
                with col:
                    times_list = []
                    for selecao in times_grupo:
                        bandeira_url = get_bandeira_url(selecao, bandeiras_dict)
                        times_list.append(f'<div style="display: flex; align-items: center; gap: 6px; padding: 5px 0; border-bottom: 1px solid #2a2a3a;"><img src="{bandeira_url}" style="width: 24px; height: auto; border-radius: 2px;"><span style="color: white; font-size: 0.75rem;">{selecao}</span></div>')
                    times_html = "".join(times_list)
                    grupo_html = f'<div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #2a2a3a; border-radius: 10px; padding: 0.8rem; margin-bottom: 0.5rem;"><div style="font-family: Bebas Neue, sans-serif; font-size: 1.1rem; color: #00ccff; text-align: center; border-bottom: 2px solid #00ccff; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">GRUPO {grupo}</div>{times_html}</div>'
                    st.markdown(grupo_html, unsafe_allow_html=True)
    
    # Tabela de dados
    st.markdown("### 📋 Dados Completos das Seleções")
    
    # Filtro por confederação
    col_conf_filtro = 'Confederação' if 'Confederação' in df_dados.columns else ('Confederacao' if 'Confederacao' in df_dados.columns else None)
    if col_conf_filtro:
        confederacoes = ['Todas'] + sorted(df_dados[col_conf_filtro].unique().tolist())
        filtro_conf = st.selectbox("Filtrar por Confederação", confederacoes, key="filtro_conf_datasets")
        
        if filtro_conf != 'Todas':
            df_display = df_dados[df_dados[col_conf_filtro] == filtro_conf].copy()
        else:
            df_display = df_dados.copy()
    else:
        df_display = df_dados.copy()
    
    st.dataframe(df_display, use_container_width=True, height=350)
    
    # Adicionar coluna Elo ao DataFrame
    df_dados['Elo'] = df_dados['Seleção'].map(elo_dict)
    
    # Gráficos de análise
    st.markdown("### 📊 Análises por Confederação e Grupo")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        fig_grupos = px.bar(
            df_dados.groupby('Grupo')['Elo'].mean().reset_index(),
            x='Grupo', y='Elo',
            color='Elo', color_continuous_scale=['#2d5a4a', '#00ff88'],
            title="💪 Rating Elo Médio por Grupo"
        )
        fig_grupos.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='#8a8a9a', title_font_color='#00ff88'
        )
        st.plotly_chart(fig_grupos, use_container_width=True)
    
    with col_g2:
        # Verificar coluna de confederação
        col_conf = 'Confederação' if 'Confederação' in df_dados.columns else ('Confederacao' if 'Confederacao' in df_dados.columns else None)
        if col_conf:
            fig_conf = px.bar(
                df_dados.groupby(col_conf)['Elo'].mean().reset_index(),
                x=col_conf, y='Elo',
                color='Elo', color_continuous_scale=['#2d4a5a', '#00ccff'],
                title="🌍 Rating Elo Médio por Confederação"
            )
            fig_conf.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_color='#8a8a9a', title_font_color='#00ccff'
            )
            st.plotly_chart(fig_conf, use_container_width=True)
        else:
            st.info("Coluna de Confederação não encontrada nos dados.")
    
    # Download
    st.download_button(
        label="⬇️ Baixar Dados das Seleções (CSV)",
        data=df_display.to_csv(index=False).encode('utf-8'),
        file_name='selecoes_copa2026.csv',
        mime='text/csv',
        key='download_selecoes'
    )

# ============ SUB-TAB 2: HISTÓRICO DE COPAS ============
with dataset_tab2:
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid rgba(255, 215, 0, 0.3); border-radius: 12px; padding: 1rem; margin: 1rem 0;">
        <div style="color: #ffd700; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">🏆 Histórico Completo das Copas do Mundo (1930-2022)</div>
        <div style="color: #8a8a9a; font-size: 0.9rem;">
            Registro histórico de todas as 22 edições da Copa do Mundo FIFA realizadas até hoje.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        if os.path.exists(CAMINHO_HISTORICO):
            df_historico = pd.read_excel(CAMINHO_HISTORICO)
            
            col_h1, col_h2, col_h3, col_h4 = st.columns(4)
            with col_h1:
                st.metric("🏆 Edições Realizadas", len(df_historico))
            with col_h2:
                if 'Campeao' in df_historico.columns:
                    campeoes_unicos = df_historico['Campeao'].nunique()
                    st.metric("🥇 Nações Campeãs", campeoes_unicos)
            with col_h3:
                if 'Ano' in df_historico.columns:
                    anos = df_historico['Ano'].max() - df_historico['Ano'].min()
                    st.metric("📅 Anos de História", f"{int(anos)}")
            with col_h4:
                if 'Sede' in df_historico.columns:
                    sedes_unicas = df_historico['Sede'].nunique()
                    st.metric("🌍 Países-Sede", sedes_unicas)
            
            st.markdown("### 📜 Todas as Edições")
            st.dataframe(df_historico, use_container_width=True, height=350)
            
            # Análise de títulos
            if 'Campeao' in df_historico.columns:
                st.markdown("### 🏆 Análise de Títulos Mundiais")
                col_hg1, col_hg2 = st.columns(2)
                
                with col_hg1:
                    titulos = df_historico['Campeao'].value_counts().reset_index()
                    titulos.columns = ['Seleção', 'Títulos']
                    
                    fig_titulos = px.bar(
                        titulos,
                        y='Seleção', x='Títulos',
                        orientation='h',
                        color='Títulos',
                        color_continuous_scale=['#cd7f32', '#ffd700'],
                        title="🥇 Ranking de Campeões Mundiais"
                    )
                    fig_titulos.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#8a8a9a', title_font_color='#ffd700',
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig_titulos, use_container_width=True)
                
                with col_hg2:
                    if 'Vice' in df_historico.columns:
                        vices = df_historico['Vice'].value_counts().reset_index()
                        vices.columns = ['Seleção', 'Vice-campeonatos']
                        
                        fig_vices = px.bar(
                            vices,
                            y='Seleção', x='Vice-campeonatos',
                            orientation='h',
                            color='Vice-campeonatos',
                            color_continuous_scale=['#5a5a5a', '#c0c0c0'],
                            title="🥈 Ranking de Vice-Campeões"
                        )
                        fig_vices.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                            font_color='#8a8a9a', title_font_color='#c0c0c0',
                            yaxis={'categoryorder': 'total ascending'}
                        )
                        st.plotly_chart(fig_vices, use_container_width=True)
            
            st.download_button(
                label="⬇️ Baixar Histórico de Copas (CSV)",
                data=df_historico.to_csv(index=False).encode('utf-8'),
                file_name='historico_copas_mundo.csv',
                mime='text/csv',
                key='download_historico'
            )
        else:
            st.warning("⚠️ Arquivo HistoricoCopas.xlsx não encontrado na pasta dataset/")
    except Exception as e:
        st.error(f"❌ Erro ao carregar Histórico de Copas: {e}")

# ============ SUB-TAB 3: RANKING ELO ============
with dataset_tab3:
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid rgba(0, 204, 255, 0.3); border-radius: 12px; padding: 1rem; margin: 1rem 0;">
        <div style="color: #00ccff; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">📈 Sistema de Rating ELO</div>
        <div style="color: #8a8a9a; font-size: 0.9rem;">
            O Rating ELO é considerado mais preciso que o Ranking FIFA para prever resultados.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        if os.path.exists(CAMINHO_ELO):
            df_elo_tab = pd.read_excel(CAMINHO_ELO)
            
            col_rating = None
            for col in ['Rating_ELO', 'ELO', 'rating', 'Rating', 'Elo']:
                if col in df_elo_tab.columns:
                    col_rating = col
                    break
            
            col_selecao = None
            for col in ['Seleção', 'Selecao', 'País', 'Pais', 'Country', 'Team']:
                if col in df_elo_tab.columns:
                    col_selecao = col
                    break
            
            col_elo1, col_elo2, col_elo3, col_elo4 = st.columns(4)
            with col_elo1:
                st.metric("🌍 Seleções Ranqueadas", len(df_elo_tab))
            with col_elo2:
                if col_rating:
                    max_elo = pd.to_numeric(df_elo_tab[col_rating], errors='coerce').max()
                    st.metric("🔝 Maior Rating", f"{max_elo:.0f}")
            with col_elo3:
                if col_rating:
                    media_elo = pd.to_numeric(df_elo_tab[col_rating], errors='coerce').mean()
                    st.metric("📊 Média Global", f"{media_elo:.0f}")
            with col_elo4:
                if col_rating:
                    desvio = pd.to_numeric(df_elo_tab[col_rating], errors='coerce').std()
                    st.metric("📐 Desvio Padrão", f"{desvio:.0f}")
            
            st.markdown("### 🏅 Ranking ELO Completo")
            st.dataframe(df_elo_tab, use_container_width=True, height=350)
            
            if col_rating and col_selecao:
                df_elo_sorted = df_elo_tab.copy()
                df_elo_sorted[col_rating] = pd.to_numeric(df_elo_sorted[col_rating], errors='coerce')
                df_elo_sorted = df_elo_sorted.dropna(subset=[col_rating])
                
                st.markdown("### 📊 Análise do Rating ELO")
                col_eg1, col_eg2 = st.columns(2)
                
                with col_eg1:
                    top15 = df_elo_sorted.nlargest(15, col_rating)
                    fig_elo_top = px.bar(
                        top15,
                        y=col_selecao, x=col_rating,
                        orientation='h',
                        color=col_rating,
                        color_continuous_scale=['#1a3a5c', '#00ccff'],
                        title="🏆 Top 15 - Rating ELO Mundial"
                    )
                    fig_elo_top.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#8a8a9a', title_font_color='#00ccff',
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig_elo_top, use_container_width=True)
                
                with col_eg2:
                    fig_dist = px.histogram(
                        df_elo_sorted,
                        x=col_rating,
                        nbins=20,
                        color_discrete_sequence=['#00ccff'],
                        title="📈 Distribuição dos Ratings ELO"
                    )
                    fig_dist.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#8a8a9a', title_font_color='#00ccff'
                    )
                    st.plotly_chart(fig_dist, use_container_width=True)
            
            st.download_button(
                label="⬇️ Baixar Ranking ELO (CSV)",
                data=df_elo_tab.to_csv(index=False).encode('utf-8'),
                file_name='ranking_elo_copa2026.csv',
                mime='text/csv',
                key='download_elo'
            )
        else:
            st.warning("⚠️ Arquivo RankingElo6Dez.xlsx não encontrado na pasta dataset/")
    except Exception as e:
        st.error(f"❌ Erro ao carregar Ranking ELO: {e}")

# ============ SUB-TAB 4: TABELA DE JOGOS ============
with dataset_tab4:
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid rgba(255, 0, 255, 0.3); border-radius: 12px; padding: 1rem; margin: 1rem 0;">
        <div style="color: #ff00ff; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">📅 Calendário Oficial - Copa do Mundo 2026</div>
        <div style="color: #8a8a9a; font-size: 0.9rem;">
            A Copa 2026 será a primeira com 48 seleções, realizada em 3 países: 🇺🇸 EUA, 🇨🇦 Canadá e 🇲🇽 México.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        if os.path.exists(CAMINHO_JOGOS):
            df_jogos = pd.read_excel(CAMINHO_JOGOS)
            
            col_j1, col_j2, col_j3, col_j4 = st.columns(4)
            with col_j1:
                st.metric("⚽ Total de Jogos", len(df_jogos))
            with col_j2:
                if 'Fase' in df_jogos.columns:
                    fases = df_jogos['Fase'].nunique()
                    st.metric("📊 Fases", fases)
            with col_j3:
                col_cidade = next((c for c in ['Cidade', 'Sede', 'City'] if c in df_jogos.columns), None)
                if col_cidade:
                    cidades = df_jogos[col_cidade].nunique()
                    st.metric("🏙️ Cidades-Sede", cidades)
            with col_j4:
                col_estadio = next((c for c in ['Estádio', 'Estadio', 'Stadium'] if c in df_jogos.columns), None)
                if col_estadio:
                    estadios = df_jogos[col_estadio].nunique()
                    st.metric("🏟️ Estádios", estadios)
            
            st.markdown("### 📋 Calendário Completo de Jogos")
            st.dataframe(df_jogos, use_container_width=True, height=350)
            
            st.download_button(
                label="⬇️ Baixar Tabela de Jogos (CSV)",
                data=df_jogos.to_csv(index=False).encode('utf-8'),
                file_name='tabela_jogos_copa2026.csv',
                mime='text/csv',
                key='download_jogos'
            )
        else:
            st.warning("⚠️ Arquivo TabelaJogos.xlsx não encontrado na pasta dataset/")
    except Exception as e:
        st.error(f"❌ Erro ao carregar Tabela de Jogos: {e}")




