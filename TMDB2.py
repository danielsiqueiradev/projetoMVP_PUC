import pandas as pd #type: ignore
import requests
import time
import os
from dotenv import load_dotenv # type: ignore



print("1. Abrindo a base de ouro completa...")
df_kinoplex = pd.read_csv('Resultado_Kinoplex_Por_Complexo.csv', sep=';', encoding='utf-8')

# --- A MÁGICA DO FILTRO DOS 5K NO PANDAS ---
print("2. Passando a faca: Calculando o somatório total de cada filme...")

# Agrupa por filme e soma todos os ingressos de todos os cinemas e datas
publico_total_filme = df_kinoplex.groupby('TITULO_ORIGINAL')['PUBLICO'].sum()

# Pega a lista com os nomes dos filmes que bateram a meta de 5000
filmes_de_sucesso = publico_total_filme[publico_total_filme >= 5000].index

# Filtra a base original pra manter APENAS as linhas desses filmes brabos
df_kinoplex_filtrado = df_kinoplex[df_kinoplex['TITULO_ORIGINAL'].isin(filmes_de_sucesso)].copy()

print(f"Limpeza feita! A base caiu de {len(df_kinoplex)} para {len(df_kinoplex_filtrado)} linhas úteis.")

# Salva essa base filtrada pra ser a nossa nova base oficial de faturamento
df_kinoplex_filtrado.to_csv('Resultado_Kinoplex_5k_Mais.csv', index=False, sep=';', encoding='utf-8-sig')


# --- A BUSCA NA API DO TMDB ---
# Agora pega só os nomes únicos dessa base já filtrada pra buscar na internet
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

    # Pesquisar o ID do filme
    url_search = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={titulo}&language=pt-BR"
    
    try:
        resp_search = requests.get(url_search).json()
        
        if resp_search.get('results') and len(resp_search['results']) > 0:
            filme_info = resp_search['results'][0]
            movie_id = filme_info['id']
            
            # Pegar os detalhes (Gêneros e Ano)
            url_details = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=pt-BR"
            resp_details = requests.get(url_details).json()
            
            generos = [g['name'] for g in resp_details.get('genres', [])]
            ano_lancamento = str(resp_details.get('release_date', ''))[:4]
            
            # Pegar a Classificação Indicativa BR
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
                'CLASSIFICACAO': classificacao
            })
            
        else:
            dados_tmdb.append({
                'TITULO_ORIGINAL': titulo,
                'GENEROS': "Nao Encontrado",
                'ANO_LANCAMENTO': "Nao Encontrado",
                'CLASSIFICACAO': "Nao Encontrado"
            })
            
    except Exception as e:
        print(f"Deu ruim na requisição do filme '{titulo}': {e}")
    
    # Freio pra API não banir a gente (0.15 segundos)
    time.sleep(0.15)

# Transforma os resultados numa tabela e salva
df_tmdb = pd.DataFrame(dados_tmdb)
df_tmdb.to_csv('Base_TMDB_Filmes.csv', index=False, sep=';', encoding='utf-8-sig')

print("\n🚀 Show, rodou liso! Base do TMDB fresquinha salva com sucesso!")