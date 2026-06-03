import os
import requests
from dotenv import load_dotenv # type: ignore


load_dotenv()

api_key_tmdb = os.getenv("TMDB_API_KEY")
api_key_omdb = os.getenv("OMDB_API_KEY")

# Simulando que a gente já pescou esse ID lá no primeiro passo
id_filme_tmdb = 1523898 

print("1. Perguntando pro TMDB qual é o ID desse filme lá no concorrente (IMDb)...")

# Endpoint de DETALHES do TMDB
url_detalhes = f"https://api.themoviedb.org/3/movie/{id_filme_tmdb}?api_key={api_key_tmdb}&language=pt-BR"
response_tmdb = requests.get(url_detalhes).json()

# Puxando o ID mágico (se não tiver, ele salva como None)
id_imdb = response_tmdb.get('imdb_id')

if id_imdb:
    print(f"Achei, cria! O RG do filme no IMDb é: {id_imdb}")
    print("2. Batendo na OMDb direto no alvo... 🎯\n")
    
    # Olha o pulo do gato aqui: usamos '?i=' em vez de '?t='
    url_omdb = f"http://www.omdbapi.com/?i={id_imdb}&apikey={api_key_omdb}"
    response_omdb = requests.get(url_omdb).json()
    
    if response_omdb.get('Response') == 'True':
        nota_imdb = response_omdb.get('imdbRating', 'N/A')
        nota_metacritic = response_omdb.get('Metascore', 'N/A')
        nome = response_omdb.get('Title', 'N/A')
        ano = response_omdb.get('Year', 'N/A')
        
        nota_rotten = "N/A"
        for avaliacao in response_omdb.get('Ratings', []):
            if avaliacao['Source'] == 'Rotten Tomatoes':
                nota_rotten = avaliacao['Value']
                break
                
        print("--- 🍅 TERMÔMETRO DA CRÍTICA (À PROVA DE FALHAS) ---")
        print(f" Nome Filme: {nome}")
        print(f" Ano: {ano}")
        print(f" Nota IMDb: {nota_imdb}")
        print(f" Rotten Tomatoes: {nota_rotten}")
        print(f" Metacritic: {nota_metacritic}")
        print("-" * 46)
    else:
        print("OMDb não liberou a ficha pra esse ID.")
else:
    print("Deu ruim. O TMDB ainda não cadastrou o ID do IMDb pra esse filme.")
print(response_omdb)