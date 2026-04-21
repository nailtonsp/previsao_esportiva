import streamlit as st
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import inject_custom_css, get_bandeira_url
from utils.data_loader import carregar_dados, carregar_dados_elo, preparar_estruturas
from utils.config import CAMINHO_DADOS

# Injetar CSS
inject_custom_css()

# ============ HEADER ============
st.markdown('<h1 class="main-title">⚽ COPA 2026 SIMULATOR</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Simulação Monte Carlo • Análise de Probabilidades • FIFA World Cup USA/CAN/MEX</p>', unsafe_allow_html=True)
st.markdown("---")

# ============ CARREGAR DADOS ============
try:
    df_dados = carregar_dados()
    df_elo = carregar_dados_elo()
    selecoes, elo_dict, grupos_dict, bandeiras_dict, stats_gols_dict = preparar_estruturas(df_dados, df_elo)
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

# ============ BEM-VINDO ============
st.markdown("""
<div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid rgba(0, 255, 136, 0.3); border-radius: 16px; padding: 2rem; margin: 1rem 0;">
    <div style="text-align: center;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🏆</div>
        <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; color: #00ff88; margin-bottom: 0.5rem;">
            Bem-vindo ao Copa 2026 Simulator
        </div>
        <div style="color: #8a8a9a; font-size: 1.1rem; max-width: 700px; margin: 0 auto;">
            Este simulador utiliza <b style="color: #00ccff;">Métodos Monte Carlo</b> para calcular 
            probabilidades de cada seleção em todas as fases da Copa do Mundo 2026.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============ ESTATÍSTICAS RÁPIDAS ============
st.markdown("### 📊 Visão Geral da Copa 2026")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">48</div>
        <div class="stat-label">Seleções</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">12</div>
        <div class="stat-label">Grupos</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">104</div>
        <div class="stat-label">Jogos</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">3</div>
        <div class="stat-label">Países Sede</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============ FUNCIONALIDADES ============
st.markdown("### 🚀 Funcionalidades Disponíveis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border-left: 4px solid #00ff88; padding: 1.5rem; margin: 0.5rem 0; border-radius: 0 12px 12px 0;">
        <div style="color: #00ff88; font-size: 1.5rem; margin-bottom: 0.5rem;">📋 Datasets</div>
        <div style="color: #8a8a9a;">Explore os dados das seleções, histórico de copas, ranking Elo e calendário de jogos.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border-left: 4px solid #00ccff; padding: 1.5rem; margin: 0.5rem 0; border-radius: 0 12px 12px 0;">
        <div style="color: #00ccff; font-size: 1.5rem; margin-bottom: 0.5rem;">🎮 Simulação</div>
        <div style="color: #8a8a9a;">Execute simulações Monte Carlo com diferentes metodologias e parâmetros.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border-left: 4px solid #ffd700; padding: 1.5rem; margin: 0.5rem 0; border-radius: 0 12px 12px 0;">
        <div style="color: #ffd700; font-size: 1.5rem; margin-bottom: 0.5rem;">📊 Resultados</div>
        <div style="color: #8a8a9a;">Análise detalhada dos resultados com gráficos, tabelas e exportação de dados.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border-left: 4px solid #ff00ff; padding: 1.5rem; margin: 0.5rem 0; border-radius: 0 12px 12px 0;">
        <div style="color: #ff00ff; font-size: 1.5rem; margin-bottom: 0.5rem;">🎬 Ao Vivo</div>
        <div style="color: #8a8a9a;">Acompanhe uma Copa do Mundo simulada jogo a jogo em tempo real.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border-left: 4px solid #ff6b6b; padding: 1.5rem; margin: 0.5rem 0; border-radius: 0 12px 12px 0;">
        <div style="color: #ff6b6b; font-size: 1.5rem; margin-bottom: 0.5rem;">💰 Odds Implícitas</div>
        <div style="color: #8a8a9a;">Compare as probabilidades do mercado com os resultados da simulação.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border-left: 4px solid #4a9aff; padding: 1.5rem; margin: 0.5rem 0; border-radius: 0 12px 12px 0;">
        <div style="color: #4a9aff; font-size: 1.5rem; margin-bottom: 0.5rem;">⚔️ Simulador de Partida</div>
        <div style="color: #8a8a9a;">Simule confrontos individuais e veja probabilidades de placares.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============ TOP 5 FAVORITOS ============
st.markdown("### 🏆 Top 5 Favoritos (por Rating Elo)")

# Adicionar coluna Elo ao DataFrame
df_dados['Elo'] = df_dados['Seleção'].map(elo_dict)
top5 = df_dados.nlargest(5, 'Elo')

for idx, (_, row) in enumerate(top5.iterrows()):
    pos = idx + 1
    medalha = "🥇" if pos == 1 else ("🥈" if pos == 2 else ("🥉" if pos == 3 else f"#{pos}"))
    cor = '#ffd700' if pos == 1 else ('#c0c0c0' if pos == 2 else ('#cd7f32' if pos == 3 else '#00ff88'))
    conf = row.get('Confederação', row.get('Confederacao', 'N/A'))
    
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, #1e1e2e, #16161f); border-left: 4px solid {cor}; padding: 0.8rem 1rem; margin: 0.3rem 0; border-radius: 0 8px 8px 0; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5rem;">{medalha}</span>
            <img src="{get_bandeira_url(row['Seleção'], bandeiras_dict)}" style="width: 36px; border-radius: 4px;">
            <div>
                <span style="color: white; font-size: 1.1rem; font-weight: 600;">{row['Seleção']}</span>
                <span style="color: #8a8a9a; font-size: 0.85rem; margin-left: 10px;">{conf} • Grupo {row['Grupo']}</span>
            </div>
        </div>
        <span style="color: {cor}; font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem;">{row['Elo']:.0f}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============ COMO USAR ============
st.markdown("### 📖 Como Usar")

st.markdown("""
<div style="background: linear-gradient(145deg, #1a1a2e, #12121a); border: 1px solid #2a2a3a; border-radius: 12px; padding: 1.5rem;">
    <ol style="color: #e0e0e0; line-height: 2;">
        <li>📋 <b>Explore os Datasets</b> - Conheça as seleções, histórico e rankings</li>
        <li>⚙️ <b>Configure a Simulação</b> - Use a barra lateral para ajustar parâmetros</li>
        <li>🎮 <b>Execute a Simulação</b> - Rode milhares de simulações Monte Carlo</li>
        <li>📊 <b>Analise os Resultados</b> - Veja probabilidades, gráficos e estatísticas</li>
        <li>🎬 <b>Simule Ao Vivo</b> - Acompanhe uma Copa completa jogo a jogo</li>
        <li>⚔️ <b>Compare Seleções</b> - Use o Simulador de Partida para confrontos diretos</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
<p style="text-align: center; color: #4a4a5a; font-size: 0.85rem;">
    ⚽ Copa 2026 Simulator • Monte Carlo Simulation Engine • Built with Streamlit
</p>
""", unsafe_allow_html=True)




