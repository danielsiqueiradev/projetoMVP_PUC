import pandas as pd #type: ignore
import requests
import time
import os
from dotenv import load_dotenv # type: ignore

print("1. Abrindo a base de ouro completa...")
df_kinoplex = pd.read_csv('Resultado_Kinoplex_Por_Complexo.csv', sep=';', encoding='utf-8')

# --- A MÁGICA DO FILTRO DOS 5K NO PANDAS ---
print("2. Passando a faca: Calculando o somatório total de cada filme...")

publico_total_filme = df_kinoplex.groupby('TITULO_ORIGINAL')['PUBLICO'].sum()
filmes_de_sucesso = publico_total_filme[publico_total_filme >= 5000].index
df_kinoplex_filtrado = df_kinoplex[df_kinoplex['TITULO_ORIGINAL'].isin(filmes_de_sucesso)].copy()

print(f"Limpeza feita! A base caiu de {len(df_kinoplex)} para {len(df_kinoplex_filtrado)} linhas úteis.")
df_kinoplex_filtrado.to_csv('Resultado_Kinoplex_5k_Mais.csv', index=False, sep=';', encoding='utf-8-sig')


# --- A BUSCA NA API DO TMDB (AGORA COM ORÇAMENTO) ---
filmes_unicos = df_kinoplex_filtrado['TITULO_ORIGINAL'].dropna().str.strip().unique()
print(f"\nTotal de filmes de peso na agulha pra buscar no TMDB: {len(filmes_unicos)}")

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY") 

dados_tmdb = []
contador = 0

print("3. Iniciando a caçada no TMDB... (Vai tomar uma água que isso demora um cadinho)")

for titulo in filmes_unicos:
    contador += 1
    if contador % 50 == 0:
        print(f"Já fomos {contador} filmes de {len(filmes_unicos)}...")

    url_search = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={titulo}&language=pt-BR"
    
    try:
        resp_search = requests.get(url_search).json()
        
        if resp_search.get('results') and len(resp_search['results']) > 0:
            filme_info = resp_search['results'][0]
            movie_id = filme_info['id']
            
            # -------------------------------------------------------------
            # O PULO DO GATO É AQUI: O endpoint details já traz o budget!
            # -------------------------------------------------------------
            url_details = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=pt-BR"
            resp_details = requests.get(url_details).json()
            
            generos = [g['name'] for g in resp_details.get('genres', [])]
            ano_lancamento = str(resp_details.get('release_date', ''))[:4]
            
            # --- PEGANDO O ORÇAMENTO (E tratando zeros) ---
            orcamento = resp_details.get('budget', 0)
            
            url_release = f"https://api.themoviedb.org/3/movie/{movie_id}/release_dates?api_key={API_KEY}"
            resp_release = requests.get(url_release).json()
            
            classificacao = "Sem Classificacao"
            for country in resp_release.get('results', []):
                if country['iso_3166_1'] == 'BR':
                    for cert in country['release_dates']:
                        if cert.get('certification'):
                            classificacao = cert.get('certification')
                            break
                    break
            
            dados_tmdb.append({
                'TITULO_ORIGINAL': titulo,
                'GENEROS': ", ".join(generos),
                'ANO_LANCAMENTO': ano_lancamento,
                'CLASSIFICACAO': classificacao,
                'ORCAMENTO_USD': orcamento  # <--- NOVA COLUNA AQUI!
            })
            
        else:
            dados_tmdb.append({
                'TITULO_ORIGINAL': titulo,
                'GENEROS': "Nao Encontrado",
                'ANO_LANCAMENTO': "Nao Encontrado",
                'CLASSIFICACAO': "Nao Encontrado",
                'ORCAMENTO_USD': 0 # <--- ZERADO SE NÃO ACHAR
            })
            
    except Exception as e:
        print(f"Deu ruim na requisição do filme '{titulo}': {e}")
    
    time.sleep(0.15)

df_tmdb = pd.DataFrame(dados_tmdb)
df_tmdb.to_csv('Base_TMDB_Filmes_Com_Orcamento.csv', index=False, sep=';', encoding='utf-8-sig')

print("\n🚀 Show, rodou liso! Base do TMDB fresquinha (e milionária) salva com sucesso!")