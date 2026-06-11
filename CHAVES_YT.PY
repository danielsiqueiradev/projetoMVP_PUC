import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from transformers import pipeline

load_dotenv()

# ==========================================
# 🚨 MALANDRAGEM: SÓ AS CHAVES ENTRE ASPAS
# ==========================================
CHAVES_YOUTUBE = [
    "AIzaSyAewXN7pAhGnbIou7kIDDRvQsjGJ9I_IAs",
    "AIzaSyDq0HbmWBIc62uOfF67xZbGG7hKylQsZsY",
    "AIzaSyDq0HbmWBIc62uOfF67xZbGG7hKylQsZsY",
    "AIzaSyDq0HbmWBIc62uOfF67xZbGG7hKylQsZsY",
    "AIzaSyAY-RgEqpTrbQ1BUQc4Gme8y_lJQrA9p9g",
    "AIzaSyAQGSb8mR-8BDwp1dc50cflwZ06RuK8LsM",
    "AIzaSyB9DSjONJYkFF81tBtBeAdweb8Tx_bpaz0",
    "AIzaSyDvNWHjWWFLU0QoVHMzuoaMcBx3yxyJNiA"
]
indice_chave_yt = 0

def get_youtube_service():
    return build('youtube', 'v3', developerKey=CHAVES_YOUTUBE[indice_chave_yt])

youtube = get_youtube_service()

try:
    analisador = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
except: pass
OMDB_KEY = os.getenv("OMDB_API_KEY")

def get_omdb_rating(titulo):
    try:
        url = f"http://www.omdbapi.com/?t={titulo}&apikey={OMDB_KEY}"
        res = requests.get(url)
        if res.status_code in [401, 429]: raise Exception("API_LIMIT_OMDB")
        data = res.json()
        for r in data.get('Ratings', []):
            if r['Source'] == 'Rotten Tomatoes': return float(r['Value'].replace('%', ''))
        return 0.0
    except: return 0.0

def get_youtube_data(titulo, yt_service):
    try:
        search = yt_service.search().list(q=f"{titulo} trailer oficial", part='id', type='video', maxResults=1).execute()
        if not search['items']: return 0.0, 0.0, 0.0
        
        v_id = search['items'][0]['id']['videoId']
        stats = yt_service.videos().list(part='statistics', id=v_id).execute()['items'][0]['statistics']
        v = float(stats.get('viewCount', 0))
        l = float(stats.get('likeCount', 0))
        
        s = 0.0
        try:
            coments = yt_service.commentThreads().list(part='snippet', videoId=v_id, maxResults=5).execute()
            textos = [c['snippet']['topLevelComment']['snippet']['textDisplay'] for c in coments['items']]
            if textos:
                notas = [float(analisador(t)[0]['label'].split()[0]) for t in textos]
                s = sum(notas) / len(notas)
        except HttpError as e_com:
            if "commentsDisabled" in str(e_com):
                print(" 😶 [Comentários Off] ", end="")
            elif e_com.resp.status in [403, 429]:
                raise Exception("API_LIMIT_YOUTUBE")
                
        return v, l, s
    except HttpError as e:
        if e.resp.status in [403, 429] and "commentsDisabled" not in str(e):
            raise Exception("API_LIMIT_YOUTUBE")
        return 0.0, 0.0, 0.0
    except: 
        return 0.0, 0.0, 0.0

def salvar_checkpoint(df, dicionario, arquivo, titulo_unicos):
    """Função blindada pra salvar no meio do caminho sem tu perder nada"""
    df_temp = df.copy()
    for t in titulo_unicos:
        if t not in dicionario:
            dicionario[t] = {'rt': 0.0, 'views': 0.0, 'likes': 0.0, 'sent': 0.0}
    df_temp['rotten_tomatoes'] = df_temp['TITULO_ORIGINAL'].map(lambda x: dicionario[x]['rt'])
    df_temp['yt_views'] = df_temp['TITULO_ORIGINAL'].map(lambda x: dicionario[x]['views'])
    df_temp['yt_likes'] = df_temp['TITULO_ORIGINAL'].map(lambda x: dicionario[x]['likes'])
    df_temp['yt_sentiment'] = df_temp['TITULO_ORIGINAL'].map(lambda x: dicionario[x]['sent'])
    df_temp.to_csv(arquivo, index=False, encoding='utf-8-sig')

def fiscal_blindado():
    global youtube, indice_chave_yt
    arquivo = "Base_Kinoplex_ML_Final_Patched.csv"
    
    df = pd.read_csv(arquivo, encoding='utf-8-sig')
    filmes_unicos = df['TITULO_ORIGINAL'].unique()
    
    print("🔍 FASE 1: Vasculhando a base pra ver o que já temos salvo...")
    dicionario_dados = {}
    filmes_para_baixar = []
    
    for titulo in filmes_unicos:
        subset = df[df['TITULO_ORIGINAL'] == titulo]
        max_views = subset['yt_views'].max()
        if max_views > 0:
            linha_boa = subset[subset['yt_views'] > 0].iloc[0]
            dicionario_dados[titulo] = {
                'rt': linha_boa['rotten_tomatoes'],
                'views': linha_boa['yt_views'],
                'likes': linha_boa['yt_likes'],
                'sent': linha_boa['yt_sentiment']
            }
        else:
            filmes_para_baixar.append(titulo)
            
    print(f"✅ Já temos os dados de {len(dicionario_dados)} filmes na agulha.")
    print(f"⚠️ Faltam baixar {len(filmes_para_baixar)} filmes. Partiu!")
    
    print("\n🌐 FASE 2: Iniciando download com Checkpoint...")
    limite_atingido = False
    
    for i, titulo in enumerate(filmes_para_baixar):
        print(f"[{i+1}/{len(filmes_para_baixar)}] Baixando: {titulo}", end="")
        rt = get_omdb_rating(titulo)
        
        sucesso_yt = False
        while not sucesso_yt:
            try:
                v, l, s = get_youtube_data(titulo, youtube)
                dicionario_dados[titulo] = {'rt': rt, 'views': v, 'likes': l, 'sent': s}
                sucesso_yt = True
                print(" ✅")
                time.sleep(0.5) 
                
            except Exception as e:
                if "API_LIMIT_YOUTUBE" in str(e):
                    indice_chave_yt += 1
                    if indice_chave_yt < len(CHAVES_YOUTUBE):
                        print(f"\n🔄 Cota esgotada! Trocando para a chave {indice_chave_yt + 1}...")
                        youtube = get_youtube_service() 
                    else:
                        print("\n❌ CAÔ! Todas as chaves foram pro saco.")
                        limite_atingido = True
                        sucesso_yt = True
                else:
                    dicionario_dados[titulo] = {'rt': rt, 'views': 0.0, 'likes': 0.0, 'sent': 0.0}
                    sucesso_yt = True
                    print(" ❌ Erro Desconhecido")

        # 🚨 A MÁGICA DO CHECKPOINT: Salva a cada 50 filmes!
        if (i + 1) % 50 == 0:
            print(f"💾 [CHECKPOINT] Salvando o progresso dos {i+1} filmes pra tu não perder nada...")
            salvar_checkpoint(df, dicionario_dados, arquivo, filmes_unicos)

        if limite_atingido:
            break

    print("\n🚀 FASE 3: Imputando os valores finais...")
    salvar_checkpoint(df, dicionario_dados, arquivo, filmes_unicos)
    
    if limite_atingido:
        print("\n⚠️ Salvo! Acabaram as tuas chaves, mas tudo até aqui foi gravado no arquivo!")
    else:
        print("\n✅ VRAU! Zeramos a lista. A base tá brilhando!")

if __name__ == "__main__":
    fiscal_blindado()