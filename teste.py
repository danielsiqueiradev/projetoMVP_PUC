import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build

# 1. SETUP
load_dotenv()
youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))

# Funções (mantendo as mesmas que a gente já testou)
def get_omdb_rating(titulo):
    url = f"http://www.omdbapi.com/?t={titulo}&apikey={os.getenv('OMDB_API_KEY')}"
    try:
        data = requests.get(url).json()
        for r in data.get('Ratings', []):
            if r['Source'] == 'Rotten Tomatoes':
                return float(r['Value'].replace('%', ''))
        return 0.0
    except: return 0.0

def get_youtube_data(titulo):
    try:
        search_res = youtube.search().list(q=f"{titulo} trailer oficial", part='id', type='video', maxResults=1).execute()
        if not search_res['items']: return 0.0, 0.0
        
        video_id = search_res['items'][0]['id']['videoId']
        stats_res = youtube.videos().list(part='statistics', id=video_id).execute()
        stats = stats_res['items'][0]['statistics']
        return float(stats.get('viewCount', 0)), float(stats.get('likeCount', 0))
    except:
        return 0.0, 0.0

# 2. SCRIPT DE RESGATE
def resumir_base():
    # LÊ O QUE JÁ FOI FEITO
    df = pd.read_csv("Base_Kinoplex_ML_Final.csv")
    
    print(f"🚀 Iniciando resgate de dados...")
    
    for i, row in df.iterrows():
        # A MÁGICA: Só roda se o valor for zero
        if df.at[i, 'rotten_tomatoes'] != 0.0 or df.at[i, 'yt_views'] != 0.0:
            continue
        
        titulo = row['TITULO_ORIGINAL']
        print(f"[{i+1}/{len(df)}] Resgatando: {titulo}")
        
        # Busca apenas o que falta
        rt = get_omdb_rating(titulo)
        views, likes = get_youtube_data(titulo)
        
        df.at[i, 'rotten_tomatoes'] = rt
        df.at[i, 'yt_views'] = views
        df.at[i, 'yt_likes'] = likes
        
        # Salva a cada 10 filmes pra não ter erro
        if (i + 1) % 10 == 0:
            df.to_csv("Base_Kinoplex_ML_Final.csv", index=False)
            print("--- Progresso salvo no arquivo principal! ---")
            
        time.sleep(1.5)

    df.to_csv("Base_Kinoplex_ML_Final.csv", index=False)
    print("\n✅ Agora sim! Base completada.")

if __name__ == "__main__":
    resumir_base()