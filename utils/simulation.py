# ============ FUNÇÕES DE SIMULAÇÃO ============
import numpy as np
from scipy.stats import poisson

from utils.config import MEDIA_GOLS_COPA

# ============ PARÂMETROS DO MODELO ELO-POISSON ============
ELO_SCALE_DEFAULT = 400  # K padrão: 400 pts diferença = 10x força
MEDIA_GLOBAL_PADRAO = 1.375  # Metade de 2.75 (média por time)
FATOR_AMORTECIMENTO = 1.0  # C = 1 para regressão à média (50/50)

# ============ CORREÇÃO DIXON-COLES ============
def dixon_coles_correction(gols_casa, gols_fora, lambda_casa, lambda_fora, rho=-0.13):
    """
    Aplica a correção de Dixon-Coles para placares baixos.
    
    A correção:
    - AUMENTA probabilidade de: 0-0 e 1-1 (mais empates)
    - DIMINUI probabilidade de: 1-0 e 0-1 (menos vitórias magras)
    
    O parâmetro ρ (rho) é tipicamente negativo (-0.13 a -0.10).
    """
    if gols_casa == 0 and gols_fora == 0:
        return 1 - lambda_casa * lambda_fora * rho
    elif gols_casa == 0 and gols_fora == 1:
        return 1 + lambda_casa * rho
    elif gols_casa == 1 and gols_fora == 0:
        return 1 + lambda_fora * rho
    elif gols_casa == 1 and gols_fora == 1:
        return 1 - rho
    else:
        return 1.0

def calcular_media_dinamica(gf_a, gs_a, gf_b, gs_b, media_liga_base=MEDIA_GOLS_COPA, amortecimento=FATOR_AMORTECIMENTO):
    """
    Calcula a média de gols esperada dinamicamente baseada nas estatísticas de cada time.
    
    Metodologia:
    1. Calcula forças de ataque/defesa relativas à média da liga
    2. Aplica amortecimento para evitar valores extremos (regressão à média)
    3. Cruza ataque de A com defesa de B e vice-versa
    
    Parâmetros:
    - gf_a, gs_a: Média de gols feitos e sofridos do Time A
    - gf_b, gs_b: Média de gols feitos e sofridos do Time B
    - media_liga_base: Média total de gols na liga (default 2.75)
    - amortecimento: Fator C de regressão à média (C=1 → 50/50 com média)
    
    Retorna:
    - m_total: Média total de gols esperados na partida
    - m_a: Média de gols esperados do Time A
    - m_b: Média de gols esperados do Time B
    """
    # Média por time (metade da média do jogo)
    media_global = media_liga_base / 2
    
    # Forças Relativas (Bruta)
    atq_a_bruto = gf_a / media_global if media_global > 0 else 1.0
    def_a_bruto = gs_a / media_global if media_global > 0 else 1.0
    atq_b_bruto = gf_b / media_global if media_global > 0 else 1.0
    def_b_bruto = gs_b / media_global if media_global > 0 else 1.0
    
    # Aplicar amortecimento (regressão à média)
    # Fórmula: (Força + C) / (1 + C)
    atq_a = (atq_a_bruto + amortecimento) / (1 + amortecimento)
    def_a = (def_a_bruto + amortecimento) / (1 + amortecimento)
    atq_b = (atq_b_bruto + amortecimento) / (1 + amortecimento)
    def_b = (def_b_bruto + amortecimento) / (1 + amortecimento)
    
    # Cruzamento: Ataque A x Defesa B (e vice-versa)
    m_a = atq_a * def_b * media_global
    m_b = atq_b * def_a * media_global
    
    # Garantir valores mínimos razoáveis
    m_a = max(0.3, min(4.0, m_a))
    m_b = max(0.3, min(4.0, m_b))
    
    m_total = m_a + m_b
    
    return m_total, m_a, m_b

def elo_to_forca(elo, k_scale=ELO_SCALE_DEFAULT):
    """
    Transforma o rating Elo em "Força" usando função exponencial.
    
    Fórmula: f = 10^(Elo/K)
    
    Isso garante que uma diferença de K pontos (ex: 400) 
    resulta em uma proporção de 10:1 na força.
    
    Exemplo com K=400:
    - Elo 2000 vs Elo 1600 → diferença 400 → razão 10:1
    """
    return 10 ** (elo / k_scale)

def calcular_lambdas_poisson(elo_a, elo_b, media_gols=MEDIA_GOLS_COPA, k_scale=ELO_SCALE_DEFAULT):
    """
    Calcula as médias de Poisson (λ) usando o Ranking Elo (modo ESTÁTICO).
    
    Metodologia:
    1. Converte Elo em Força: f = 10^(Elo/K)
    2. Calcula proporção: peso₁ = f₁ / (f₁ + f₂)
    3. Distribui gols: m₁ = m × peso₁, m₂ = m - m₁
    
    Parâmetros:
    - elo_a, elo_b: Ratings Elo das seleções
    - media_gols: Média total de gols esperada (m = m₁ + m₂)
    - k_scale: Fator de escala (400 = padrão Elo, onde 400 pts = 10x força)
    """
    # Transformar Elo em Força Exponencial
    f_a = elo_to_forca(elo_a, k_scale)
    f_b = elo_to_forca(elo_b, k_scale)
    
    # Calcular proporção de força
    soma_forcas = f_a + f_b
    peso_a = f_a / soma_forcas
    
    # Distribuir gols conforme a proporção
    lambda_a = media_gols * peso_a
    lambda_b = media_gols - lambda_a
    
    # Garantir valores mínimos
    lambda_a = max(0.1, lambda_a)
    lambda_b = max(0.1, lambda_b)
    
    return lambda_a, lambda_b

def calcular_lambdas_poisson_dinamico(elo_a, elo_b, stats_a, stats_b, k_scale=ELO_SCALE_DEFAULT, media_base=MEDIA_GOLS_COPA, amortecimento=FATOR_AMORTECIMENTO):
    """
    Calcula as médias de Poisson (λ) usando Elo + Estatísticas (modo DINÂMICO).
    
    Metodologia Híbrida:
    1. Calcula média TOTAL da partida via estatísticas de GF/GS (dinâmico)
    2. Usa o Elo para DISTRIBUIR essa média entre os times (proporção)
    
    Parâmetros:
    - elo_a, elo_b: Ratings Elo das seleções
    - stats_a: tuple (gols_feitos_media, gols_sofridos_media) do Time A
    - stats_b: tuple (gols_feitos_media, gols_sofridos_media) do Time B
    - k_scale: Fator de escala Elo
    - media_base: Média base da liga (para referência)
    - amortecimento: Fator de regressão à média
    
    Retorna:
    - lambda_a, lambda_b: médias de Poisson
    - m_total: média total calculada dinamicamente
    """
    gf_a, gs_a = stats_a
    gf_b, gs_b = stats_b
    
    # 1. Calcular média TOTAL dinâmica baseada nas estatísticas
    m_total, _, _ = calcular_media_dinamica(gf_a, gs_a, gf_b, gs_b, media_base, amortecimento)
    
    # 2. Usar Elo para distribuir a média (quem deve fazer mais gols)
    f_a = elo_to_forca(elo_a, k_scale)
    f_b = elo_to_forca(elo_b, k_scale)
    
    soma_forcas = f_a + f_b
    peso_a = f_a / soma_forcas
    
    # 3. Distribuir o bolo dinâmico conforme proporção do Elo
    lambda_a = m_total * peso_a
    lambda_b = m_total - lambda_a
    
    # Garantir valores mínimos
    lambda_a = max(0.1, lambda_a)
    lambda_b = max(0.1, lambda_b)
    
    return lambda_a, lambda_b, m_total

def simular_jogo(elo_a, elo_b, mata_mata=False, config=None, stats_a=None, stats_b=None):
    """
    Simula um jogo entre duas seleções usando Elo + Poisson.
    
    Gera gols aleatórios:
    - Gols_A ~ Poisson(λ₁)
    - Gols_B ~ Poisson(λ₂)
    
    Onde λ é derivado do Elo transformado.
    
    Modo Dinâmico:
    - Se stats_a e stats_b forem fornecidos E modo_dinamico=True no config,
      a média de gols é calculada dinamicamente baseada em GF/GS.
    """
    if config is None:
        config = {}
    
    media_gols = config.get('media_gols', MEDIA_GOLS_COPA)
    k_scale = config.get('k_scale', ELO_SCALE_DEFAULT)
    usar_dixon_coles = config.get('usar_dixon_coles', False)
    rho = config.get('rho_dixon_coles', -0.13)
    modo_dinamico = config.get('modo_dinamico', False)
    amortecimento = config.get('amortecimento', FATOR_AMORTECIMENTO)
    
    # Calcular lambdas
    if modo_dinamico and stats_a is not None and stats_b is not None:
        # Modo dinâmico: média baseada em estatísticas
        lambda_a, lambda_b, _ = calcular_lambdas_poisson_dinamico(
            elo_a, elo_b, stats_a, stats_b, k_scale, media_gols, amortecimento
        )
    else:
        # Modo estático: média fixa
        lambda_a, lambda_b = calcular_lambdas_poisson(elo_a, elo_b, media_gols, k_scale)
    
    # Gerar gols com distribuição de Poisson
    gols_a = np.random.poisson(lambda_a)
    gols_b = np.random.poisson(lambda_b)
    
    # Aplicar correção Dixon-Coles se ativada
    if usar_dixon_coles:
        correcao = dixon_coles_correction(gols_a, gols_b, lambda_a, lambda_b, rho)
        if correcao < 1.0 and np.random.random() > correcao:
            gols_a = np.random.poisson(lambda_a)
            gols_b = np.random.poisson(lambda_b)
    
    # Fair-play (critério de desempate)
    fp_a, fp_b = -np.random.poisson(1.5), -np.random.poisson(1.5)
    
    # Determinar resultado
    if gols_a > gols_b: 
        return 3, 0, gols_a, gols_b, fp_a, fp_b, 0  # Vitória A
    if gols_b > gols_a: 
        return 0, 3, gols_a, gols_b, fp_a, fp_b, 1  # Vitória B
    if not mata_mata:   
        return 1, 1, gols_a, gols_b, fp_a, fp_b, -1  # Empate (fase grupos)
    
    # Mata-mata: pênaltis (probabilidade baseada no Elo)
    f_a = elo_to_forca(elo_a, k_scale)
    f_b = elo_to_forca(elo_b, k_scale)
    prob_a_vencer = f_a / (f_a + f_b)
    return 0, 0, gols_a, gols_b, fp_a, fp_b, 0 if np.random.random() < prob_a_vencer else 1

def simular_fase_grupos(grupos_dict, elo_dict, config=None, stats_gols_dict=None):
    """Simula a fase de grupos"""
    resultados = []
    for grupo, times in grupos_dict.items():
        stats = {t: [0, 0, 0, 0] for t in times}
        for i in range(len(times)):
            for j in range(i + 1, len(times)):
                t1, t2 = times[i], times[j]
                # Obter estatísticas de gols se disponíveis
                stats_t1 = stats_gols_dict.get(t1) if stats_gols_dict else None
                stats_t2 = stats_gols_dict.get(t2) if stats_gols_dict else None
                
                p1, p2, ga, gb, fp1, fp2, _ = simular_jogo(
                    elo_dict[t1], elo_dict[t2], 
                    config=config, 
                    stats_a=stats_t1, 
                    stats_b=stats_t2
                )
                stats[t1][0] += p1; stats[t1][1] += ga - gb; stats[t1][2] += ga; stats[t1][3] += fp1
                stats[t2][0] += p2; stats[t2][1] += gb - ga; stats[t2][2] += gb; stats[t2][3] += fp2
        ranking = sorted(stats.items(), key=lambda x: (x[1][0], x[1][1], x[1][2], x[1][3]), reverse=True)
        for pos, (selecao, stat) in enumerate(ranking):
            resultados.append((selecao, grupo, pos + 1, stat[0], stat[1], stat[2], stat[3]))
    return resultados

def definir_classificados_32(resultados_grupos, elo_dict):
    """Define os 32 classificados para o mata-mata"""
    primeiros = [(t, s[0], s[1], s[2], s[3]) for t, g, p, *s in resultados_grupos if p == 1]
    segundos = [(t, s[0], s[1], s[2], s[3]) for t, g, p, *s in resultados_grupos if p == 2]
    terceiros = sorted([(t, s[0], s[1], s[2], s[3]) for t, g, p, *s in resultados_grupos if p == 3],
                       key=lambda x: (x[1], x[2], x[3], x[4]), reverse=True)[:8]
    todos = primeiros + segundos + terceiros
    return sorted(todos, key=lambda x: (x[1], x[2], x[3], elo_dict[x[0]]), reverse=True)

def rodar_mata_mata(classificados, elo_dict, historico, fase, confrontos, config=None, stats_gols_dict=None):
    """Simula fase mata-mata recursivamente"""
    if len(classificados) < 2:
        return classificados
    
    vencedores = []
    n = len(classificados)
    
    participantes_fase = [c[0] for c in classificados]
    
    if fase == 4:
        confrontos['quartas'] = tuple(sorted(participantes_fase))
    elif fase == 5:
        confrontos['semis'] = tuple(sorted(participantes_fase))
    elif fase == 6:
        confrontos['final'] = tuple(sorted(participantes_fase))
    
    for i in range(n // 2):
        t1, t2 = classificados[i][0], classificados[n - 1 - i][0]
        # Obter estatísticas de gols se disponíveis
        stats_t1 = stats_gols_dict.get(t1) if stats_gols_dict else None
        stats_t2 = stats_gols_dict.get(t2) if stats_gols_dict else None
        
        *_, resultado = simular_jogo(
            elo_dict[t1], elo_dict[t2], 
            mata_mata=True, 
            config=config,
            stats_a=stats_t1,
            stats_b=stats_t2
        )
        ganhador = t1 if resultado == 0 else t2
        dados = classificados[i] if resultado == 0 else classificados[n - 1 - i]
        vencedores.append(dados)
        historico[ganhador][fase] = 1
    
    return rodar_mata_mata(vencedores, elo_dict, historico, fase + 1, confrontos, config, stats_gols_dict)

def simular_uma_copa(selecoes, elo_dict, grupos_dict, config=None, poderes_dict=None, stats_gols_dict=None):
    """Simula uma Copa completa"""
    historico = {t: [0] * 7 for t in selecoes}
    confrontos = {'quartas': None, 'semis': None, 'final': None}
    
    resultados = simular_fase_grupos(grupos_dict, elo_dict, config, stats_gols_dict)
    for t, *_ in resultados:
        historico[t][0] = 1
    
    classificados = definir_classificados_32(resultados, elo_dict)
    for t, *_ in classificados:
        historico[t][1] = 1
    
    rodar_mata_mata(classificados, elo_dict, historico, 2, confrontos, config, stats_gols_dict)
    return historico, confrontos

def calcular_probabilidades_partida(elo_1, elo_2, media_gols=MEDIA_GOLS_COPA, k_scale=ELO_SCALE_DEFAULT, 
                                     max_gols=8, usar_dixon_coles=False, rho=-0.13):
    """
    Calcula as probabilidades de cada placar usando Elo + Poisson.
    
    Metodologia:
    1. Converte Elo em Força: f = 10^(Elo/K)
    2. Calcula λ₁ = m × f₁/(f₁+f₂), λ₂ = m - λ₁
    3. Para cada placar: P(i,j) = P(X=i) × P(Y=j)
    4. Se Dixon-Coles ativo, aplica correção para 0-0, 1-0, 0-1, 1-1
    5. Soma probabilidades por resultado (V/E/D)
    """
    lambda_1, lambda_2 = calcular_lambdas_poisson(elo_1, elo_2, media_gols, k_scale)
    
    # Matriz de probabilidades
    prob_matrix = np.zeros((max_gols + 1, max_gols + 1))
    
    for gols1 in range(max_gols + 1):
        for gols2 in range(max_gols + 1):
            prob_base = poisson.pmf(gols1, lambda_1) * poisson.pmf(gols2, lambda_2)
            
            if usar_dixon_coles:
                correcao = dixon_coles_correction(gols1, gols2, lambda_1, lambda_2, rho)
                prob_base *= correcao
            
            prob_matrix[gols1, gols2] = prob_base
    
    # Normalizar
    prob_matrix = prob_matrix / prob_matrix.sum()
    
    # Calcular probabilidades de resultado
    prob_vitoria_1 = 0
    prob_empate = 0
    prob_vitoria_2 = 0
    
    for gols1 in range(max_gols + 1):
        for gols2 in range(max_gols + 1):
            if gols1 > gols2:
                prob_vitoria_1 += prob_matrix[gols1, gols2]
            elif gols1 == gols2:
                prob_empate += prob_matrix[gols1, gols2]
            else:
                prob_vitoria_2 += prob_matrix[gols1, gols2]
    
    return prob_matrix, lambda_1, lambda_2, prob_vitoria_1, prob_empate, prob_vitoria_2

def calcular_probabilidades_partida_dinamico(elo_1, elo_2, stats_1, stats_2, k_scale=ELO_SCALE_DEFAULT,
                                               media_base=MEDIA_GOLS_COPA, amortecimento=FATOR_AMORTECIMENTO,
                                               max_gols=8, usar_dixon_coles=False, rho=-0.13):
    """
    Calcula as probabilidades de cada placar usando Elo + Poisson (modo DINÂMICO).
    
    Usa estatísticas de GF/GS para calcular a média total da partida dinamicamente.
    """
    lambda_1, lambda_2, m_total = calcular_lambdas_poisson_dinamico(
        elo_1, elo_2, stats_1, stats_2, k_scale, media_base, amortecimento
    )
    
    # Matriz de probabilidades
    prob_matrix = np.zeros((max_gols + 1, max_gols + 1))
    
    for gols1 in range(max_gols + 1):
        for gols2 in range(max_gols + 1):
            prob_base = poisson.pmf(gols1, lambda_1) * poisson.pmf(gols2, lambda_2)
            
            if usar_dixon_coles:
                correcao = dixon_coles_correction(gols1, gols2, lambda_1, lambda_2, rho)
                prob_base *= correcao
            
            prob_matrix[gols1, gols2] = prob_base
    
    # Normalizar
    prob_matrix = prob_matrix / prob_matrix.sum()
    
    # Calcular probabilidades de resultado
    prob_vitoria_1 = 0
    prob_empate = 0
    prob_vitoria_2 = 0
    
    for gols1 in range(max_gols + 1):
        for gols2 in range(max_gols + 1):
            if gols1 > gols2:
                prob_vitoria_1 += prob_matrix[gols1, gols2]
            elif gols1 == gols2:
                prob_empate += prob_matrix[gols1, gols2]
            else:
                prob_vitoria_2 += prob_matrix[gols1, gols2]
    
    return prob_matrix, lambda_1, lambda_2, prob_vitoria_1, prob_empate, prob_vitoria_2, m_total

def calcular_razao_forca(elo_1, elo_2, k_scale=ELO_SCALE_DEFAULT):
    """
    Calcula a razão de força entre duas seleções baseado no Elo.
    
    Retorna quantas vezes a seleção 1 é "mais forte" que a seleção 2.
    Com K=400, diferença de 400 pts = razão 10:1
    """
    f1 = elo_to_forca(elo_1, k_scale)
    f2 = elo_to_forca(elo_2, k_scale)
    return f1 / f2 if f2 > 0 else float('inf')




