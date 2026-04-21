import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import inject_custom_css, get_bandeira_url, get_bandeira_html, get_brasil_style
from utils.data_loader import carregar_dados, carregar_dados_elo, preparar_estruturas
from utils.config import CAMINHO_ODDS

inject_custom_css()

st.markdown("## 💰 Probabilidades Implícitas das Casas de Apostas")
st.markdown("""
<p style="color: #8a8a9a; font-size: 1rem; margin-bottom: 1.5rem;">
    As probabilidades implícitas são calculadas a partir das odds atuais oferecidas pelas casas de apostas.<br>
    Elas representam a <b style="color: #00ff88;">percepção do mercado</b> sobre as chances de cada seleção ser campeã.
</p>
""", unsafe_allow_html=True)

# Carregar dados
try:
    df_dados = carregar_dados()
    df_elo = carregar_dados_elo()
    selecoes, elo_dict, grupos_dict, bandeiras_dict, stats_gols_dict = preparar_estruturas(df_dados, df_elo)
except Exception as e:
    st.error(f"❌ Erro ao carregar dados base: {e}")
    st.stop()

# Carregar odds
try:
    df_odds = pd.read_csv(CAMINHO_ODDS, decimal=',')
    df_odds.columns = ['Seleção', 'Prob_Implicita']
    df_odds['Prob_Implicita'] = pd.to_numeric(df_odds['Prob_Implicita'], errors='coerce')
    df_odds['Prob_Percentual'] = df_odds['Prob_Implicita'] * 100
    df_odds['Odds_Decimal'] = 1 / df_odds['Prob_Implicita']
    df_odds = df_odds.sort_values('Prob_Implicita', ascending=False).reset_index(drop=True)
    df_odds['Posição'] = df_odds.index + 1
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(df_odds)}</div>
            <div class="stat-label">Seleções Cotadas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        favorito = df_odds.iloc[0]
        fav_bandeira = get_bandeira_url(favorito['Seleção'], bandeiras_dict)
        st.markdown(f"""
        <div class="stat-card">
            <img src="{fav_bandeira}" style="width: 48px; border-radius: 4px; margin-bottom: 0.5rem;">
            <div class="stat-value" style="font-size: 2rem;">{favorito['Seleção']}</div>
            <div class="stat-label">Favorito das Casas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{favorito['Prob_Percentual']:.1f}%</div>
            <div class="stat-label">Prob. do Favorito</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        soma_probs = df_odds['Prob_Implicita'].sum()
        margem = (soma_probs - 1) * 100
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{margem:.1f}%</div>
            <div class="stat-label">Margem da Casa</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top 3 Favoritos
    st.markdown("### 🏆 Top 3 Favoritos do Mercado")
    
    col1, col2, col3 = st.columns(3)
    top3_odds = df_odds.head(3)
    
    with col1:
        sel1 = top3_odds.iloc[0]['Seleção']
        st.markdown(f"""
        <div class="team-card gold">
            <div class="team-rank gold">🥇</div>
            <div class="team-name">{get_bandeira_html(sel1, bandeiras_dict, 32)}{sel1}</div>
            <div class="team-prob">{top3_odds.iloc[0]['Prob_Percentual']:.1f}%</div>
        </div>
        <div style="text-align: center; color: #8a8a9a; font-size: 0.9rem; margin-top: 0.5rem;">
            Odds: {top3_odds.iloc[0]['Odds_Decimal']:.2f}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        sel2 = top3_odds.iloc[1]['Seleção']
        st.markdown(f"""
        <div class="team-card silver">
            <div class="team-rank silver">🥈</div>
            <div class="team-name">{get_bandeira_html(sel2, bandeiras_dict, 32)}{sel2}</div>
            <div class="team-prob">{top3_odds.iloc[1]['Prob_Percentual']:.1f}%</div>
        </div>
        <div style="text-align: center; color: #8a8a9a; font-size: 0.9rem; margin-top: 0.5rem;">
            Odds: {top3_odds.iloc[1]['Odds_Decimal']:.2f}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        sel3 = top3_odds.iloc[2]['Seleção']
        st.markdown(f"""
        <div class="team-card bronze">
            <div class="team-rank bronze">🥉</div>
            <div class="team-name">{get_bandeira_html(sel3, bandeiras_dict, 32)}{sel3}</div>
            <div class="team-prob">{top3_odds.iloc[2]['Prob_Percentual']:.1f}%</div>
        </div>
        <div style="text-align: center; color: #8a8a9a; font-size: 0.9rem; margin-top: 0.5rem;">
            Odds: {top3_odds.iloc[2]['Odds_Decimal']:.2f}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.markdown("### 📊 Top 15 - Probabilidades Implícitas")
        
        top15_odds = df_odds.head(15).iloc[::-1]
        
        fig_odds_bar = go.Figure()
        fig_odds_bar.add_trace(go.Bar(
            y=top15_odds['Seleção'],
            x=top15_odds['Prob_Percentual'],
            orientation='h',
            marker=dict(
                color=top15_odds['Prob_Percentual'],
                colorscale=[[0, '#ff6b6b'], [0.3, '#ffd700'], [1, '#00ff88']],
                line=dict(width=0)
            ),
            text=[f"{v:.1f}%" for v in top15_odds['Prob_Percentual']],
            textposition='outside',
            textfont=dict(color='#00ff88', size=12)
        ))
        
        fig_odds_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#8a8a9a',
            height=500,
            xaxis_title="Probabilidade Implícita (%)",
            yaxis_title="",
            margin=dict(l=100, r=80)
        )
        st.plotly_chart(fig_odds_bar, use_container_width=True)
    
    with col_graf2:
        st.markdown("### 🎯 Distribuição de Probabilidades")
        
        def categorizar(prob):
            if prob >= 10:
                return "Alta (≥10%)"
            elif prob >= 5:
                return "Média-Alta (5-10%)"
            elif prob >= 1:
                return "Média (1-5%)"
            elif prob >= 0.5:
                return "Baixa (0.5-1%)"
            else:
                return "Muito Baixa (<0.5%)"
        
        df_odds['Categoria'] = df_odds['Prob_Percentual'].apply(categorizar)
        cat_counts = df_odds['Categoria'].value_counts().reindex([
            "Alta (≥10%)", "Média-Alta (5-10%)", "Média (1-5%)", "Baixa (0.5-1%)", "Muito Baixa (<0.5%)"
        ]).fillna(0)
        
        fig_pie = go.Figure(go.Pie(
            labels=cat_counts.index,
            values=cat_counts.values,
            hole=0.5,
            marker=dict(colors=['#00ff88', '#00ccff', '#ffd700', '#ff9f43', '#ff6b6b']),
            textinfo='label+value',
            textfont=dict(size=11)
        ))
        
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#8a8a9a',
            height=500,
            showlegend=False,
            annotations=[dict(text='Seleções', x=0.5, y=0.5, font_size=16, showarrow=False, font_color='#00ff88')]
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # Tabela completa
    st.markdown("### 📋 Tabela Completa de Probabilidades")
    
    df_display_odds = df_odds[['Posição', 'Seleção', 'Prob_Percentual', 'Odds_Decimal']].copy()
    df_display_odds.columns = ['#', 'Seleção', 'Probabilidade (%)', 'Odds Decimal']
    df_display_odds['Probabilidade (%)'] = df_display_odds['Probabilidade (%)'].apply(lambda x: f"{x:.2f}%")
    df_display_odds['Odds Decimal'] = df_display_odds['Odds Decimal'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(df_display_odds, use_container_width=True, height=400, hide_index=True)
    
    # Comparação com simulação
    if 'resultado' in st.session_state:
        st.markdown("---")
        st.markdown("### 🔄 Comparação: Mercado vs Simulação Monte Carlo")
        
        df_sim = st.session_state['resultado'].copy()
        df_sim['Seleção'] = df_sim.index
        df_sim['Prob_Simulacao'] = df_sim['Campeão'] * 100
        
        df_compare = df_odds.merge(df_sim[['Seleção', 'Prob_Simulacao']], on='Seleção', how='inner')
        df_compare['Diferença'] = df_compare['Prob_Simulacao'] - df_compare['Prob_Percentual']
        df_compare = df_compare.sort_values('Prob_Percentual', ascending=False).head(15)
        
        fig_compare = go.Figure()
        
        fig_compare.add_trace(go.Bar(
            name='Odds Implícitas',
            x=df_compare['Seleção'],
            y=df_compare['Prob_Percentual'],
            marker_color='#ff6b6b',
            text=[f"{v:.1f}%" for v in df_compare['Prob_Percentual']],
            textposition='outside'
        ))
        
        fig_compare.add_trace(go.Bar(
            name='Simulação Monte Carlo',
            x=df_compare['Seleção'],
            y=df_compare['Prob_Simulacao'],
            marker_color='#00ff88',
            text=[f"{v:.1f}%" for v in df_compare['Prob_Simulacao']],
            textposition='outside'
        ))
        
        fig_compare.update_layout(
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#8a8a9a',
            height=450,
            xaxis_title="",
            yaxis_title="Probabilidade (%)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_compare, use_container_width=True)
        
        # Value bets
        st.markdown("### 💎 Value Bets (Simulação > Mercado)")
        st.markdown('<p style="color: #8a8a9a;">Seleções onde nossa simulação dá mais chances do que o mercado.</p>', unsafe_allow_html=True)
        
        value_bets = df_compare[df_compare['Diferença'] > 0.5].sort_values('Diferença', ascending=False)
        
        if len(value_bets) > 0:
            for _, row in value_bets.iterrows():
                sel_name = row['Seleção']
                brasil_style_vb = get_brasil_style(sel_name)
                cor_borda_vb = '#009c3b' if brasil_style_vb['is_brasil'] else '#00ff88'
                extra_vb = brasil_style_vb['glow'] if brasil_style_vb['is_brasil'] else ''
                cor_txt = '#ffd700' if brasil_style_vb['is_brasil'] else 'white'
                
                st.markdown(f"""
                <div class="team-card" style="border-left-color: {cor_borda_vb}; {extra_vb}">
                    <div class="team-name" style="color: {cor_txt};">{get_bandeira_html(sel_name, bandeiras_dict, 28)}{sel_name}</div>
                    <div style="color: {cor_borda_vb}; font-size: 1.2rem;">
                        +{row['Diferença']:.1f}% acima do mercado
                    </div>
                    <div style="color: #8a8a9a; font-size: 0.9rem;">
                        Mercado: {row['Prob_Percentual']:.1f}% | Simulação: {row['Prob_Simulacao']:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum value bet encontrado com diferença significativa.")

except FileNotFoundError:
    st.error(f"❌ Arquivo `{CAMINHO_ODDS}` não encontrado!")
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {str(e)}")




