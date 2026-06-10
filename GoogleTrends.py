import pandas as pd #type: ignore
from pytrends.request import TrendReq #type: ignore
import praw #type: ignore

# --- CONFIGURAÇÕES REDDIT ---
reddit = praw.Reddit(
    client_id="TEU_ID_REDDIT",
    client_secret="TEU_SECRET_REDDIT",
    user_agent="Kinobot_v1_por_Daniel"
)

# --- CONFIGURAÇÕES GOOGLE TRENDS ---
pytrends = TrendReq(hl='pt-BR', tz=360)

print("🚀 Iniciando a Varredura Final: Google Trends + Reddit...")

# 1. PEGANDO O HYPE NO GOOGLE (0 a 100)
kw_list = ["The Sheep Detectives"] # Título do filme
pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='BR', gprop='')
interesse_busca = pytrends.interest_over_time()

# Pegamos a média de interesse da última semana
score_hype_google = int(interesse_busca[kw_list[0]].mean()) if not interesse_busca.empty else 0

# 2. PEGANDO O SENTIMENTO NO REDDIT
print(f"Buscando o que os nerds do Reddit acham de {kw_list[0]}...")
posts_reddit = []
for submission in reddit.subreddit("movies").search(kw_list[0], limit=5, sort="relevance"):
    posts_reddit.append(submission.title)

resumo_reddit = " | ".join(posts_reddit) if posts_reddit else "Sem discussões relevantes"

# 3. JUNTANDO TUDO PRO PANDAS
dados_finais = {
    "Filme": "As Ovelhas Detetives",
    "Score_Google_Trends": score_hype_google,
    "Principais_Discussões_Reddit": resumo_reddit
}

df = pd.DataFrame([dados_finais])
df.to_csv("master_data_bilheteria.csv", index=False, sep=";")

print("\n🎯 MISSÃO CUMPRIDA, PAIZÃO!")
print(f"Interesse no Google: {score_hype_google}/100")
print("Tabela 'master_data_bilheteria.csv' atualizada com o Hype das redes!")