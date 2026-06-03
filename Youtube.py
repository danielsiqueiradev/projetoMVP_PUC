import os
import requests
from dotenv import load_dotenv #type: ignore

load_dotenv()

api_key_tmdb = os.getenv("TMDB_API_KEY")
api_key_youtube = os.getenv("YOURUBE_API_KEY")

# 2. BATE NO TMDB PRA PEGAR O FILME
url_filmes = f"https://api.themoviedb.org/3/movie/upcoming?api_key={api_key_tmdb}&language=pt-BR&region=BR"
response_filmes = requests.get(url_filmes)

if response_filmes.status_code == 200:
    dados_filmes = response_filmes.json()
    filme_alvo = dados_filmes['results'][0]
    id_filme = filme_alvo['id']
    titulo = filme_alvo['title']
    
    print(f"🎬 Alvo fixado: {titulo}")
    
    # 3. BATE NOS VÍDEOS DO TMDB PRA ACHAR O TRAILER
    url_videos = f"https://api.themoviedb.org/3/movie/{id_filme}/videos?api_key={api_key_tmdb}&language=pt-BR"
    response_videos = requests.get(url_videos)
    
    chave_youtube = None
    
    if response_videos.status_code == 200:
        for video in response_videos.json()['results']:
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                chave_youtube = video['key']
                break
                
    # 4. A HORA DA VERDADE: BATE NO GOOGLE PRA MEDIR O HYPE
    if chave_youtube:
        print("Trailer encontrado! Sugando os dados do YouTube... 🧛‍♂️\n")
        
        # O endpoint do YouTube pedindo as estatísticas (part=statistics)
        url_youtube = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={chave_youtube}&key={api_key_youtube}"
        response_yt = requests.get(url_youtube)
        
        if response_yt.status_code == 200:
            dados_yt = response_yt.json()
            
            # O YouTube guarda os dados dentro da gaveta 'items' (pegamos o 1º item)
            # e depois dentro da gaveta 'statistics'
            estatisticas = dados_yt['items'][0]['statistics']
            
            views = estatisticas.get('viewCount', '0')
            likes = estatisticas.get('likeCount', '0')
            comentarios = estatisticas.get('commentCount', '0')
            
            print("--- 📊 TERMÔMETRO DO HYPE ---")
            print(f"👀 Visualizações: {views}")
            print(f"👍 Curtidas: {likes}")
            print(f"💬 Comentários: {comentarios}")
            print("-" * 30)
            print("Missão cumprida, chefe! Os dados tão na mão pra ir pro SQL.")
            
        else:
            print(f"O segurança do Google barrou! Erro {response_yt.status_code}")
    else:
        print("Nenhum trailer oficial no YouTube encontrado pelo TMDB.")
else:
    print("O segurança do TMDB barrou logo na entrada!")