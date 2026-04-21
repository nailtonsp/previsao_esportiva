import streamlit as st

# ============ CONFIGURAÇÃO DA PÁGINA ============
st.set_page_config(
    page_title="Copa 2026 Simulator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ DEFINIÇÃO DAS PÁGINAS ============
home = st.Page("pages/1_home.py", title="Home", icon="🏠", default=True)
datasets = st.Page("pages/2_datasets.py", title="Datasets", icon="📋")
simulacao = st.Page("pages/3_simulacao.py", title="Simulação", icon="🎮")
resultados = st.Page("pages/4_resultados.py", title="Resultados", icon="📊")
ao_vivo = st.Page("pages/5_ao_vivo.py", title="Ao Vivo", icon="🎬")
odds_implicitas = st.Page("pages/6_odds_implicitas.py", title="Odds Implícitas", icon="💰")
simulador_partida = st.Page("pages/7_simulador_partida.py", title="Simulador de Partida", icon="⚔️")

# ============ NAVEGAÇÃO ============
pg = st.navigation(
    {
        "Principal": [home],
        "Dados": [datasets],
        "Simulações": [simulacao, resultados, ao_vivo],
        "Análises": [odds_implicitas, simulador_partida],
    }
)

# ============ EXECUTAR PÁGINA SELECIONADA ============
pg.run()
