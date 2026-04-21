# ============ FUNÇÕES AUXILIARES ============
import streamlit as st
import numpy as np

def get_brasil_style(selecao, cor_padrao='#00ff88'):
    """Retorna estilos especiais se a seleção for Brasil"""
    if selecao == 'Brasil':
        return {
            'borda': '#009c3b',
            'bg': 'linear-gradient(145deg, #009c3b22, #ffd70015)',
            'glow': 'box-shadow: 0 0 15px rgba(0, 156, 59, 0.4), 0 0 25px rgba(255, 215, 0, 0.2);',
            'badge': '🇧🇷',
            'extra_class': 'brasil-glow',
            'is_brasil': True
        }
    return {
        'borda': cor_padrao,
        'bg': 'linear-gradient(145deg, #1e1e2e, #16161f)',
        'glow': '',
        'badge': '',
        'extra_class': '',
        'is_brasil': False
    }

def get_bandeira_html(selecao, bandeiras_dict, tamanho=24):
    """Retorna HTML da bandeira de uma seleção"""
    url = bandeiras_dict.get(selecao, 'https://flagcdn.com/w320/un.png')
    return f'<img src="{url}" style="width: {tamanho}px; height: auto; border-radius: 3px; vertical-align: middle; margin-right: 8px;">'

def get_bandeira_url(selecao, bandeiras_dict):
    """Retorna URL da bandeira de uma seleção"""
    return bandeiras_dict.get(selecao, 'https://flagcdn.com/w320/un.png')

def calcular_entropia(probabilidades):
    """Calcula a entropia de Shannon (incerteza do torneio)"""
    probs = probabilidades[probabilidades > 0]
    return -np.sum(probs * np.log2(probs))

def calcular_numero_efetivo_candidatos(probabilidades):
    """Número efetivo de candidatos (inverso do índice Herfindahl)"""
    return 1 / np.sum(probabilidades ** 2)

def calcular_indice_gini(probabilidades):
    """Índice de Gini para medir concentração"""
    sorted_probs = np.sort(probabilidades)
    n = len(sorted_probs)
    cumulative = np.cumsum(sorted_probs)
    return (2 * np.sum((np.arange(1, n + 1) * sorted_probs)) - (n + 1) * np.sum(sorted_probs)) / (n * np.sum(sorted_probs))

# ============ CSS CUSTOMIZADO ============
def inject_custom_css():
    """Injeta o CSS customizado na página"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;600;700&display=swap');
        
        :root {
            --bg-dark: #0a0a0f;
            --card-bg: #12121a;
            --accent: #00ff88;
            --accent-dim: #00cc6a;
            --text-primary: #ffffff;
            --text-secondary: #8a8a9a;
            --gold: #ffd700;
            --silver: #c0c0c0;
            --bronze: #cd7f32;
        }
        
        .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0a0a0f 100%); }
        
        .main-title {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 4rem;
            background: linear-gradient(90deg, #00ff88, #00ccff, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0;
            letter-spacing: 4px;
        }
        
        .subtitle {
            font-family: 'Outfit', sans-serif;
            color: var(--text-secondary);
            text-align: center;
            font-size: 1.1rem;
            margin-top: -10px;
        }
        
        .stat-card {
            background: linear-gradient(145deg, #1a1a2e, #12121a);
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        
        .stat-value {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 3rem;
            color: #00ff88;
            line-height: 1;
        }
        
        .stat-label {
            font-family: 'Outfit', sans-serif;
            color: #8a8a9a;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .team-card {
            background: linear-gradient(145deg, #1e1e2e, #16161f);
            border-left: 4px solid #00ff88;
            padding: 1rem 1.5rem;
            margin: 0.5rem 0;
            border-radius: 0 12px 12px 0;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .team-rank { font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: #00ff88; width: 50px; }
        .team-name { font-family: 'Outfit', sans-serif; font-weight: 600; font-size: 1.2rem; color: white; flex: 1; }
        .team-prob { font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: #00ccff; }
        
        .gold { color: #ffd700 !important; border-left-color: #ffd700 !important; }
        .silver { color: #c0c0c0 !important; border-left-color: #c0c0c0 !important; }
        .bronze { color: #cd7f32 !important; border-left-color: #cd7f32 !important; }
        
        .monitor-box {
            background: #0d0d14;
            border: 1px solid #2a2a3a;
            border-radius: 12px;
            padding: 1rem;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            color: #00ff88;
            max-height: 300px;
            overflow-y: auto;
        }
        
        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, #1a1a2e, #12121a);
            border: 1px solid rgba(0, 255, 136, 0.15);
            border-radius: 12px;
            padding: 1rem;
        }
        
        div[data-testid="stMetric"] label { color: #8a8a9a !important; }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #00ff88 !important; }
        
        .stProgress > div > div { background: linear-gradient(90deg, #00ff88, #00ccff) !important; }
        
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background: #1a1a2e;
            border-radius: 8px;
            color: #8a8a9a;
            border: 1px solid #2a2a3a;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #00ff88, #00ccff) !important;
            color: #0a0a0f !important;
        }
        
        .stSelectbox > div > div { background: #1a1a2e; border-color: #2a2a3a; }
        .stSlider > div > div > div { background: #00ff88; }
        
        .stDataFrame { border-radius: 12px; overflow: hidden; }
        
        /* DESTAQUE ESPECIAL BRASIL */
        .brasil-card {
            background: linear-gradient(145deg, #009c3b22, #ffd70022, #009c3b22) !important;
            border: 2px solid #009c3b !important;
            box-shadow: 0 0 20px rgba(0, 156, 59, 0.4), 0 0 40px rgba(255, 215, 0, 0.2) !important;
            position: relative;
        }
        
        .brasil-card::before {
            content: '🇧🇷';
            position: absolute;
            top: -8px;
            right: -8px;
            font-size: 1.2rem;
        }
        
        .brasil-glow {
            animation: brasilPulse 2s ease-in-out infinite;
        }
        
        @keyframes brasilPulse {
            0%, 100% { box-shadow: 0 0 15px rgba(0, 156, 59, 0.5); }
            50% { box-shadow: 0 0 25px rgba(255, 215, 0, 0.7), 0 0 35px rgba(0, 156, 59, 0.5); }
        }
        
        /* Estilos para página Ao Vivo */
        .match-card {
            background: linear-gradient(145deg, #1a1a2e, #12121a);
            border: 1px solid #2a2a3a;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            text-align: center;
        }
        .match-teams { display: flex; justify-content: space-between; align-items: center; }
        .match-team { font-family: 'Outfit', sans-serif; font-size: 1.1rem; color: white; flex: 1; }
        .match-score { 
            font-family: 'Bebas Neue', sans-serif; 
            font-size: 2.5rem; 
            color: #00ff88;
            padding: 0 1rem;
            min-width: 100px;
        }
        .match-info { font-size: 0.8rem; color: #8a8a9a; margin-top: 0.5rem; }
        .group-header {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.5rem;
            color: #00ccff;
            border-bottom: 2px solid #00ccff;
            padding-bottom: 0.3rem;
            margin: 1rem 0;
        }
        .phase-title {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 2rem;
            color: #ff00ff;
            text-align: center;
            margin: 1.5rem 0;
        }
        .winner-card {
            background: linear-gradient(145deg, #2a2a1e, #1a1a0f);
            border: 2px solid #ffd700;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { box-shadow: 0 0 20px #ffd700; }
            to { box-shadow: 0 0 40px #ffd700, 0 0 60px #ffa500; }
        }
        .champion-name {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 3rem;
            color: #ffd700;
        }
        .history-card {
            background: linear-gradient(145deg, #16162a, #0f0f1a);
            border: 1px solid #3a3a4a;
            border-radius: 12px;
            padding: 1.2rem;
            margin: 0.8rem 0;
            transition: all 0.3s ease;
        }
        .history-card:hover {
            border-color: #00ff88;
            transform: translateX(5px);
        }
        .history-edition {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.3rem;
            color: #00ccff;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .history-champion {
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            font-weight: 700;
            color: #ffd700;
            margin: 0.5rem 0;
        }
        .history-details {
            font-size: 0.85rem;
            color: #8a8a9a;
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 0.5rem;
        }
        .history-badge {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 20px;
            padding: 0.2rem 0.8rem;
            font-size: 0.75rem;
            color: #00ff88;
        }
        .hall-of-fame-card {
            background: linear-gradient(145deg, #1a1a0f, #2a2a1e);
            border: 2px solid #ffd700;
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            margin: 0.5rem 0;
        }
        .hall-count {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 3rem;
            color: #ffd700;
        }
        .hall-team {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 1.1rem;
            color: white;
        }
        .mini-stat {
            background: #1a1a2e;
            border-radius: 8px;
            padding: 0.8rem;
            text-align: center;
        }
        .mini-stat-value {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.8rem;
            color: #00ff88;
        }
        .mini-stat-label {
            font-size: 0.75rem;
            color: #8a8a9a;
            text-transform: uppercase;
        }
    </style>
    """, unsafe_allow_html=True)




