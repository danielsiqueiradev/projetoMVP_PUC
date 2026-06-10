import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv
from transformers import pipeline
from googleapiclient.discovery import build

# 1. CARREGAR AMBIENTE E SETUP
load_dotenv()

# Verifica se as chaves existem no .env
if not all([os.getenv("YOUTUBE_API_KEY"), os.getenv("OMDB_API_KEY"), os.getenv("HF_API_KEY")]):
    print("❌ Erro: Uma ou mais chaves de API estão faltando no teu .env!")
    exit()

youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))
# O modelo abaixo roda em português e dá notas de 1 a 5 estrelas
analisador = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

# --- FUNÇÕES DE BUSCA ---

def get_omdb_rating(titulo):
    """Busca nota no Rotten Tomatoes via OMDB."""
    url = f"http://www.omdbapi.com/?t={titulo}&apikey={os.getenv('OMDB_API_KEY')}"
    try:
        data = requests.get(url).json()
        for r in data.get('Ratings', []):
            if r['Source'] == 'Rotten Tomatoes':
                return float(r['Value'].replace('%', ''))
        return 0.0
    except: return 0.0

def get_youtube_data(titulo):
    """Busca views, likes e analisa sentimento dos comentários."""
    try:
        # Busca o vídeo
        search_res = youtube.search().list(q=f"{titulo} trailer oficial", part='id', type='video', maxResults=1).execute()
        if not search_res['items']: return 0.0, 0.0, 0.0
        
        video_id = search_res['items'][0]['id']['videoId']
        
        # Pega estatísticas
        stats_res = youtube.videos().list(part='statistics', id=video_id).execute()
        stats = stats_res['items'][0]['statistics']
        views = float(stats.get('viewCount', 0))
        likes = float(stats.get('likeCount', 0))
        
        # Pega comentários
        comments_res = youtube.commentThreads().list(part='snippet', videoId=video_id, maxResults=10).execute()
        comentarios = [c['snippet']['topLevelComment']['snippet']['textDisplay'] for c in comments_res['items']]
        
        # NLP (transforma texto em nota 1-5)
        if not comentarios: return views, likes, 0.0
        
        notas = [float(analisador(txt)[0]['label'].split()[0]) for txt in comentarios]
        avg_sentiment = sum(notas) / len(notas)
        
        return views, likes, avg_sentiment
    except:
        return 0.0, 0.0, 0.0

# --- LOOP PRINCIPAL ---

def processar_base():
    # Carrega a base blindada contra erros de formatação
    try:
        df = pd.read_csv(
            "Base_Kinoplex_ML_Pronta.csv", 
            sep=';', 
            on_bad_lines='skip', 
            engine='python', 
            encoding='utf-8-sig'
        )
    except Exception as e:
        print(f"Erro ao ler o CSV: {e}")
        return

    # Inicializa colunas como float64 para aceitar números decimais
    df['rotten_tomatoes'] = 0.0
    df['yt_views'] = 0.0
    df['yt_likes'] = 0.0
    df['yt_sentiment'] = 0.0
    
    print(f"🚀 Iniciando a varredura da base ({len(df)} filmes)...")
    
    # Processamento
    for i, row in df.iterrows():
        titulo = row['TITULO_ORIGINAL']
        print(f"[{i+1}/{len(df)}] Processando: {titulo}")
        
        rt_score = get_omdb_rating(titulo)
        v, l, s = get_youtube_data(titulo)
        
        df.at[i, 'rotten_tomatoes'] = rt_score
        df.at[i, 'yt_views'] = v
        df.at[i, 'yt_likes'] = l
        df.at[i, 'yt_sentiment'] = s
        
        # Respiro obrigatório pra API não banir
        time.sleep(1.5)
        
        # Salva o progresso a cada 50 filmes
        if (i + 1) % 50 == 0:
            df.to_csv("Base_Kinoplex_ML_Final_Progresso.csv", index=False)
            print("--- Progresso salvo! ---")
        
    df.to_csv("Base_Kinoplex_ML_Final.csv", index=False)
    print("\n✅ Show! Base finalizada e salva como 'Base_Kinoplex_ML_Final.csv'.")

if __name__ == "__main__":
    processar_base()