# ============ CONFIGURAÇÕES E CONSTANTES ============
import numpy as np

# Configurações da Simulação - Metodologia Poisson
MEDIA_GOLS_COPA = 2.75  # m = média de gols esperada por partida
FORCA_PADRAO = 1.0      # Força padrão para seleções sem dados

# Pesos para o indicador composto de força (Normalização FIFA)
PESO_RANKING_FIFA = 0.60      # 60% ranking FIFA
PESO_PARTICIPACOES = 0.15     # 15% participações em copas
PESO_MELHOR_RESULTADO = 0.25  # 25% melhor resultado histórico

# Mapeamento de nomes para o arquivo Elo
MAPEAMENTO_NOMES_ELO = {
    'Brasil': ['Brazil'],
    'Argentina': ['Argentina'],
    'França': ['France'],
    'Espanha': ['Spain'],
    'Inglaterra': ['England'],
    'Portugal': ['Portugal'],
    'Holanda': ['Netherlands', 'Holland'],
    'Alemanha': ['Germany'],
    'Bélgica': ['Belgium'],
    'Croácia': ['Croatia'],
    'Uruguai': ['Uruguay'],
    'Colômbia': ['Colombia'],
    'México': ['Mexico'],
    'Estados Unidos': ['United States', 'USA'],
    'Suíça': ['Switzerland'],
    'Japão': ['Japan'],
    'Marrocos': ['Morocco'],
    'Senegal': ['Senegal'],
    'Coreia do Sul': ['Korea Republic', 'South Korea', 'Korea Rep.'],
    'Austrália': ['Australia'],
    'Irã': ['Iran', 'IR Iran'],
    'Canadá': ['Canada'],
    'Equador': ['Ecuador'],
    'Arábia Saudita': ['Saudi Arabia'],
    'Catar': ['Qatar'],
    'Gana': ['Ghana'],
    'Costa do Marfim': ["Côte d'Ivoire", 'Ivory Coast', "Cote d'Ivoire"],
    'Tunísia': ['Tunisia'],
    'Egito': ['Egypt'],
    'Argélia': ['Algeria'],
    'Áustria': ['Austria'],
    'Escócia': ['Scotland'],
    'Noruega': ['Norway'],
    'Paraguai': ['Paraguay'],
    'Jordânia': ['Jordan'],
    'Uzbequistão': ['Uzbekistan'],
    'Panamá': ['Panama'],
    'Nova Zelândia': ['New Zealand'],
    'África do Sul': ['South Africa'],
    'Haiti': ['Haiti'],
    'Curaçau': ['Curaçao', 'Curacao'],
    'Cabo Verde': ['Cape Verde', 'Cabo Verde'],
}

# Mapeamento de melhor resultado para pontuação (0 a 1)
RESULTADO_COPA_PONTOS = {
    'Campeão': 1.0,
    '2º Lugar': 0.85,
    '3º Lugar': 0.75,
    '4º Lugar': 0.65,
    'Quartas de Final': 0.50,
    'Oitavas de Final': 0.35,
    'Fase de Grupos': 0.20,
    'Estreante': 0.10,
    'N/A': 0.10
}

# Caminho dos dados
CAMINHO_DADOS = 'dataset/DadosEnriquecidos.xlsx'
CAMINHO_ELO = 'dataset/RankingElo6Dez.xlsx'
CAMINHO_ODDS = 'dataset/probabilidades implicitas.csv'
CAMINHO_HISTORICO = 'dataset/HistoricoCopas.xlsx'
CAMINHO_JOGOS = 'dataset/TabelaJogos.xlsx'




