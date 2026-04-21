"""
Script de Coleta de Dados - Copa do Mundo FIFA 2026
====================================================
Coleta dados REAIS de APIs e websites para as 42 seleções classificadas.

Fontes:
1. REST Countries API - Dados geográficos
2. Transfermarkt - Valor de mercado, idade média
3. Wikipedia PT-BR - Resumo em português

Saída: dataset/dados_enriquecidos.csv

Autor: PrevEsport
"""

import pandas as pd
import requests
import json
import os
import time
from datetime import datetime
from bs4 import BeautifulSoup
import re

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================
DATASET_PATH = 'dataset/dados.csv'
OUTPUT_PATH = 'dataset/dados_enriquecidos.csv'
CACHE_DIR = 'dataset/cache'

os.makedirs(CACHE_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# ============================================================================
# MAPEAMENTOS COMPLETOS (42 seleções)
# ============================================================================

# Código ISO para REST Countries
CODIGO_ISO = {
    'Canadá': 'CAN', 'Estados Unidos': 'USA', 'México': 'MEX',
    'Curaçau': 'CUW', 'Haiti': 'HTI', 'Panamá': 'PAN',
    'Austrália': 'AUS', 'Arábia Saudita': 'SAU', 'Catar': 'QAT',
    'Coreia do Sul': 'KOR', 'Irã': 'IRN', 'Japão': 'JPN',
    'Jordânia': 'JOR', 'Uzbequistão': 'UZB',
    'África do Sul': 'ZAF', 'Argélia': 'DZA', 'Cabo Verde': 'CPV',
    'Costa do Marfim': 'CIV', 'Egito': 'EGY', 'Gana': 'GHA',
    'Marrocos': 'MAR', 'Senegal': 'SEN', 'Tunísia': 'TUN',
    'Argentina': 'ARG', 'Brasil': 'BRA', 'Colômbia': 'COL',
    'Equador': 'ECU', 'Paraguai': 'PRY', 'Uruguai': 'URY',
    'Nova Zelândia': 'NZL',
    'Alemanha': 'DEU', 'Áustria': 'AUT', 'Bélgica': 'BEL',
    'Croácia': 'HRV', 'Escócia': 'GBR', 'Espanha': 'ESP',
    'França': 'FRA', 'Holanda': 'NLD', 'Inglaterra': 'GBR',
    'Noruega': 'NOR', 'Portugal': 'PRT', 'Suíça': 'CHE',
}

# URLs do Transfermarkt
URLS_TRANSFERMARKT = {
    'Canadá': 'https://www.transfermarkt.com/kanada/startseite/verein/3510',
    'Estados Unidos': 'https://www.transfermarkt.com/vereinigte-staaten/startseite/verein/3505',
    'México': 'https://www.transfermarkt.com/mexiko/startseite/verein/6303',
    'Curaçau': 'https://www.transfermarkt.com/curacao/startseite/verein/23410',
    'Haiti': 'https://www.transfermarkt.com/haiti/startseite/verein/10821',
    'Panamá': 'https://www.transfermarkt.com/panama/startseite/verein/6574',
    'Austrália': 'https://www.transfermarkt.com/australien/startseite/verein/3433',
    'Arábia Saudita': 'https://www.transfermarkt.com/saudi-arabien/startseite/verein/3807',
    'Catar': 'https://www.transfermarkt.com/katar/startseite/verein/3588',
    'Coreia do Sul': 'https://www.transfermarkt.com/sudkorea/startseite/verein/3589',
    'Irã': 'https://www.transfermarkt.com/iran/startseite/verein/3582',
    'Japão': 'https://www.transfermarkt.com/japan/startseite/verein/3435',
    'Jordânia': 'https://www.transfermarkt.com/jordanien/startseite/verein/6581',
    'Uzbequistão': 'https://www.transfermarkt.com/usbekistan/startseite/verein/5724',
    'África do Sul': 'https://www.transfermarkt.com/sudafrika/startseite/verein/3806',
    'Argélia': 'https://www.transfermarkt.com/algerien/startseite/verein/3614',
    'Cabo Verde': 'https://www.transfermarkt.com/kap-verde/startseite/verein/10255',
    'Costa do Marfim': 'https://www.transfermarkt.com/cote-d-ivoire/startseite/verein/3591',
    'Egito': 'https://www.transfermarkt.com/agypten/startseite/verein/3672',
    'Gana': 'https://www.transfermarkt.com/ghana/startseite/verein/3441',
    'Marrocos': 'https://www.transfermarkt.com/marokko/startseite/verein/3575',
    'Senegal': 'https://www.transfermarkt.com/senegal/startseite/verein/3499',
    'Tunísia': 'https://www.transfermarkt.com/tunesien/startseite/verein/3670',
    'Argentina': 'https://www.transfermarkt.com/argentinien/startseite/verein/3437',
    'Brasil': 'https://www.transfermarkt.com/brasilien/startseite/verein/3439',
    'Colômbia': 'https://www.transfermarkt.com/kolumbien/startseite/verein/3816',
    'Equador': 'https://www.transfermarkt.com/ecuador/startseite/verein/5750',
    'Paraguai': 'https://www.transfermarkt.com/paraguay/startseite/verein/3581',
    'Uruguai': 'https://www.transfermarkt.com/uruguay/startseite/verein/3449',
    'Nova Zelândia': 'https://www.transfermarkt.com/neuseeland/startseite/verein/4271',
    'Alemanha': 'https://www.transfermarkt.com/deutschland/startseite/verein/3262',
    'Áustria': 'https://www.transfermarkt.com/osterreich/startseite/verein/3383',
    'Bélgica': 'https://www.transfermarkt.com/belgien/startseite/verein/3382',
    'Croácia': 'https://www.transfermarkt.com/kroatien/startseite/verein/3556',
    'Escócia': 'https://www.transfermarkt.com/schottland/startseite/verein/3380',
    'Espanha': 'https://www.transfermarkt.com/spanien/startseite/verein/3375',
    'França': 'https://www.transfermarkt.com/frankreich/startseite/verein/3377',
    'Holanda': 'https://www.transfermarkt.com/niederlande/startseite/verein/3379',
    'Inglaterra': 'https://www.transfermarkt.com/england/startseite/verein/3299',
    'Noruega': 'https://www.transfermarkt.com/norwegen/startseite/verein/3440',
    'Portugal': 'https://www.transfermarkt.com/portugal/startseite/verein/3300',
    'Suíça': 'https://www.transfermarkt.com/schweiz/startseite/verein/3384',
}

# Títulos Wikipedia em PORTUGUÊS
TITULO_WIKIPEDIA_PT = {
    'Canadá': 'Seleção_Canadense_de_Futebol_Masculino',
    'Estados Unidos': 'Seleção_Estadunidense_de_Futebol_Masculino',
    'México': 'Seleção_Mexicana_de_Futebol',
    'Curaçau': 'Seleção_Curaçauense_de_Futebol',
    'Haiti': 'Seleção_Haitiana_de_Futebol',
    'Panamá': 'Seleção_Panamenha_de_Futebol',
    'Austrália': 'Seleção_Australiana_de_Futebol_Masculino',
    'Arábia Saudita': 'Seleção_Saudita_de_Futebol',
    'Catar': 'Seleção_Catarense_de_Futebol',
    'Coreia do Sul': 'Seleção_Sul-Coreana_de_Futebol',
    'Irã': 'Seleção_Iraniana_de_Futebol',
    'Japão': 'Seleção_Japonesa_de_Futebol',
    'Jordânia': 'Seleção_Jordaniana_de_Futebol',
    'Uzbequistão': 'Seleção_Uzbeque_de_Futebol',
    'África do Sul': 'Seleção_Sul-Africana_de_Futebol',
    'Argélia': 'Seleção_Argelina_de_Futebol',
    'Cabo Verde': 'Seleção_Cabo-Verdiana_de_Futebol',
    'Costa do Marfim': 'Seleção_Marfinense_de_Futebol',
    'Egito': 'Seleção_Egípcia_de_Futebol',
    'Gana': 'Seleção_Ganesa_de_Futebol',
    'Marrocos': 'Seleção_Marroquina_de_Futebol',
    'Senegal': 'Seleção_Senegalesa_de_Futebol',
    'Tunísia': 'Seleção_Tunisiana_de_Futebol',
    'Argentina': 'Seleção_Argentina_de_Futebol',
    'Brasil': 'Seleção_Brasileira_de_Futebol',
    'Colômbia': 'Seleção_Colombiana_de_Futebol',
    'Equador': 'Seleção_Equatoriana_de_Futebol',
    'Paraguai': 'Seleção_Paraguaia_de_Futebol',
    'Uruguai': 'Seleção_Uruguaia_de_Futebol',
    'Nova Zelândia': 'Seleção_Neozelandesa_de_Futebol',
    'Alemanha': 'Seleção_Alemã_de_Futebol',
    'Áustria': 'Seleção_Austríaca_de_Futebol',
    'Bélgica': 'Seleção_Belga_de_Futebol',
    'Croácia': 'Seleção_Croata_de_Futebol',
    'Escócia': 'Seleção_Escocesa_de_Futebol',
    'Espanha': 'Seleção_Espanhola_de_Futebol',
    'França': 'Seleção_Francesa_de_Futebol',
    'Holanda': 'Seleção_Neerlandesa_de_Futebol',
    'Inglaterra': 'Seleção_Inglesa_de_Futebol',
    'Noruega': 'Seleção_Norueguesa_de_Futebol',
    'Portugal': 'Seleção_Portuguesa_de_Futebol',
    'Suíça': 'Seleção_Suíça_de_Futebol',
}

# ============================================================================
# FUNÇÕES DE CACHE
# ============================================================================

def carregar_cache(nome):
    caminho = os.path.join(CACHE_DIR, f"{nome}.json")
    if os.path.exists(caminho):
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return None

def salvar_cache(nome, dados):
    caminho = os.path.join(CACHE_DIR, f"{nome}.json")
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except:
        pass

# ============================================================================
# FONTE 1: REST Countries API
# ============================================================================

def coletar_rest_countries(selecao):
    codigo = CODIGO_ISO.get(selecao)
    if not codigo:
        return None
    
    cache = carregar_cache(f"restcountries_{codigo}")
    if cache:
        return cache
    
    try:
        url = f"https://restcountries.com/v3.1/alpha/{codigo}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()[0]
            resultado = {
                'populacao': data.get('population'),
                'area_km2': data.get('area'),
                'capital': data.get('capital', [None])[0] if data.get('capital') else None,
                'continente': data.get('continents', [None])[0] if data.get('continents') else None,
                'regiao': data.get('region'),
            }
            salvar_cache(f"restcountries_{codigo}", resultado)
            return resultado
    except Exception as e:
        print(f"    [ERRO] {e}")
    
    return None

# ============================================================================
# FONTE 2: Transfermarkt
# ============================================================================

def extrair_valor_mercado(texto):
    if not texto:
        return None
    texto = texto.lower().replace('€', '').replace(',', '.').strip()
    try:
        if 'bn' in texto:
            return round(float(re.search(r'[\d.]+', texto).group()) * 1000, 2)
        elif 'm' in texto:
            return round(float(re.search(r'[\d.]+', texto).group()), 2)
        elif 'k' in texto:
            return round(float(re.search(r'[\d.]+', texto).group()) / 1000, 2)
    except:
        pass
    return None

def coletar_transfermarkt(selecao):
    url = URLS_TRANSFERMARKT.get(selecao)
    if not url:
        return None
    
    cache = carregar_cache(f"transfermarkt_{selecao}")
    if cache:
        return cache
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            resultado = {}
            
            # Valor de mercado
            valor_elem = soup.find('a', class_='data-header__market-value-wrapper')
            if valor_elem:
                resultado['valor_mercado_milhoes'] = extrair_valor_mercado(valor_elem.get_text(strip=True))
            
            # Dados do header
            data_header = soup.find('div', class_='data-header__details')
            if data_header:
                for item in data_header.find_all('li', class_='data-header__label'):
                    texto = item.get_text(strip=True).lower()
                    content = item.find('span', class_='data-header__content')
                    if content:
                        if 'squad size' in texto:
                            try:
                                resultado['tamanho_elenco'] = int(re.search(r'\d+', content.get_text()).group())
                            except:
                                pass
                        elif 'average age' in texto:
                            try:
                                resultado['media_idade'] = float(content.get_text(strip=True).replace(',', '.'))
                            except:
                                pass
            
            if resultado:
                salvar_cache(f"transfermarkt_{selecao}", resultado)
                return resultado
                
    except Exception as e:
        print(f"    [ERRO] {e}")
    
    return None

# ============================================================================
# FONTE 3: Wikipedia PT-BR
# ============================================================================

def coletar_wikipedia_ptbr(selecao):
    titulo = TITULO_WIKIPEDIA_PT.get(selecao)
    if not titulo:
        return None
    
    cache = carregar_cache(f"wikipedia_pt_{selecao}")
    if cache:
        return cache
    
    try:
        url = "https://pt.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'titles': titulo.replace('_', ' '),
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True,
            'format': 'json',
            'redirects': 1
        }
        
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            for page_id, page_data in pages.items():
                if page_id != '-1':
                    extract = page_data.get('extract', '')
                    if extract:
                        # Limpar e truncar
                        resumo = extract.strip()
                        resumo = re.sub(r'\s+', ' ', resumo)  # Remover espaços extras
                        resumo = resumo[:800]  # Limitar tamanho
                        
                        resultado = {'resumo': resumo}
                        salvar_cache(f"wikipedia_pt_{selecao}", resultado)
                        return resultado
    except Exception as e:
        print(f"    [ERRO] {e}")
    
    return None

# ============================================================================
# PROCESSAMENTO
# ============================================================================

def main():
    print("="*70)
    print("COLETA DE DADOS - COPA DO MUNDO FIFA 2026")
    print("="*70)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Carregar dados base
    print("\n[1/4] Carregando dados base...")
    df = pd.read_csv(DATASET_PATH, sep=';', skiprows=1)
    print(f"      {len(df)} seleções carregadas")
    
    # Inicializar colunas
    novas_colunas = ['Populacao', 'Area_km2', 'Capital', 'Continente_Geo', 'Regiao',
                     'Valor_Mercado_Milhoes_EUR', 'Media_Idade', 'Tamanho_Elenco',
                     'Resumo_Wikipedia']
    for col in novas_colunas:
        df[col] = None
    
    # Processar REST Countries
    print("\n[2/4] Coletando dados geográficos (REST Countries)...")
    for idx, row in df.iterrows():
        selecao = row['Seleção']
        if 'Vaga' in selecao:
            continue
        
        dados = coletar_rest_countries(selecao)
        if dados:
            df.at[idx, 'Populacao'] = dados.get('populacao')
            df.at[idx, 'Area_km2'] = dados.get('area_km2')
            df.at[idx, 'Capital'] = dados.get('capital')
            df.at[idx, 'Continente_Geo'] = dados.get('continente')
            df.at[idx, 'Regiao'] = dados.get('regiao')
            print(f"      ✓ {selecao}")
        else:
            print(f"      ✗ {selecao}")
        time.sleep(0.3)
    
    # Processar Transfermarkt
    print("\n[3/4] Coletando dados de mercado (Transfermarkt)...")
    for idx, row in df.iterrows():
        selecao = row['Seleção']
        if 'Vaga' in selecao:
            continue
        
        dados = coletar_transfermarkt(selecao)
        if dados:
            df.at[idx, 'Valor_Mercado_Milhoes_EUR'] = dados.get('valor_mercado_milhoes')
            df.at[idx, 'Media_Idade'] = dados.get('media_idade')
            df.at[idx, 'Tamanho_Elenco'] = dados.get('tamanho_elenco')
            valor = dados.get('valor_mercado_milhoes')
            print(f"      ✓ {selecao} - €{valor}M" if valor else f"      ✓ {selecao}")
        else:
            print(f"      ✗ {selecao}")
        time.sleep(2)
    
    # Processar Wikipedia PT-BR
    print("\n[4/4] Coletando resumos (Wikipedia PT-BR)...")
    for idx, row in df.iterrows():
        selecao = row['Seleção']
        if 'Vaga' in selecao:
            continue
        
        dados = coletar_wikipedia_ptbr(selecao)
        if dados:
            df.at[idx, 'Resumo_Wikipedia'] = dados.get('resumo')
            print(f"      ✓ {selecao} ({len(dados.get('resumo', ''))} chars)")
        else:
            print(f"      ✗ {selecao}")
        time.sleep(0.5)
    
    # Calcular métricas derivadas
    print("\n[INFO] Calculando métricas derivadas...")
    
    # Valor de mercado normalizado
    max_valor = df['Valor_Mercado_Milhoes_EUR'].max()
    if pd.notna(max_valor) and max_valor > 0:
        df['Valor_Mercado_Normalizado'] = df['Valor_Mercado_Milhoes_EUR'] / max_valor
    
    # Densidade populacional
    df['Densidade_Pop'] = df['Populacao'] / df['Area_km2']
    
    # Salvar resultado
    df.to_csv(OUTPUT_PATH, index=False, sep=';', encoding='utf-8-sig')
    print(f"\n[SALVO] {OUTPUT_PATH}")
    
    # Relatório
    print("\n" + "="*70)
    print("RELATÓRIO FINAL")
    print("="*70)
    
    df_def = df[~df['Seleção'].str.contains('Vaga', na=False)]
    total = len(df_def)
    
    colunas_check = [
        ('Populacao', 'População'),
        ('Capital', 'Capital'),
        ('Valor_Mercado_Milhoes_EUR', 'Valor Mercado'),
        ('Media_Idade', 'Média Idade'),
        ('Resumo_Wikipedia', 'Resumo Wiki'),
    ]
    
    for col, nome in colunas_check:
        if col in df.columns:
            n = df_def[col].notna().sum()
            pct = n/total*100
            print(f"  {nome:<20}: {n:2d}/{total} ({pct:.0f}%)")
    
    print("\n" + "="*70)
    print("[CONCLUÍDO] Dados salvos em:", OUTPUT_PATH)
    
    return df

if __name__ == "__main__":
    main()




