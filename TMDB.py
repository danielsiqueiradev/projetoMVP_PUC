import pandas as pd # type: ignore
import requests
import time
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

api_key = os.getenv("TMDB_API_KEY")
arquivo_limpo = "Resultado_Kinoplex_5k_Mais.csv"

print("1. Puxando a base limpa da Ancine... 📚")
df_limpo = pd.read_csv(arquivo_limpo, sep=";")
total_filmes = len(df_limpo)

dados_finais = []

print(f"\n2. Ligando o motor! Partiu buscar {total_filmes} filmes no TMDB... 🚀\n")

# O loop brabo lendo a tabela inteira
for indice, linha in df_limpo.iterrows():
    nome_filme = linha['TITULO_ORIGINAL']
    publico = linha['PUBLICO']
    progresso = f"[{indice + 1}/{total_filmes}]"
    
    try:
        # Batida 1: Buscar o ID
        url_busca = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={nome_filme}&language=pt-BR"
        resposta_busca = requests.get(url_busca).json()
        
        if len(resposta_busca.get('results', [])) > 0:
            id_tmdb = resposta_busca['results'][0]['id']
            
            # Batida 2: Ficha completa (Gêneros, Elenco, Diretor, Produtoras e Datas)
            url_detalhes = f"https://api.themoviedb.org/3/movie/{id_tmdb}?api_key={api_key}&language=pt-BR&append_to_response=credits,release_dates"
            resposta_detalhes = requests.get(url_detalhes).json()
            
            # Puxando a rapaziada toda
            generos = ", ".join([g['name'] for g in resposta_detalhes.get('genres', [])])
            elenco = resposta_detalhes.get('credits', {}).get('cast', [])
            atores = ", ".join([ator['name'] for ator in elenco]) 
            
            produtoras_lista = resposta_detalhes.get('production_companies', [])
            produtoras = ", ".join([p['name'] for p in produtoras_lista])
            
            equipe = resposta_detalhes.get('credits', {}).get('crew', [])
            diretores = ", ".join([m['name'] for m in equipe if m.get('job') == 'Director'])
            
            # 1. Puxando o Ano de Lançamento
            data_completa = resposta_detalhes.get('release_date', '')
            ano_lancamento = data_completa[:4] if data_completa else "Sem Data"

            # 2. Puxando a Classificação Etária do Brasil
            classificacao = "Não Informado"
            datas_lancamento = resposta_detalhes.get('release_dates', {}).get('results', [])
            
            for pais in datas_lancamento:
                if pais.get('iso_3166_1') == 'BR':
                    for data in pais.get('release_dates', []):
                        if data.get('certification'):
                            classificacao = data.get('certification')
                            break 
                    break 
            
            print(f"{progresso} ✅ Achou: {nome_filme} | Ano: {ano_lancamento} | Idade: {classificacao}")
            
            # Guarda tudo no bolso
            dados_finais.append({
                'ID_TMDB': id_tmdb,
                'TITULO_ORIGINAL': nome_filme,
                'PUBLICO': publico,
                'ANO_LANCAMENTO': ano_lancamento,
                'CLASSIFICACAO': classificacao,
                'GENEROS': generos,
                'ATORES_PRINCIPAIS': atores,
                'DIRETORES': diretores,
                'PRODUTORAS': produtoras
            })
            
        else:
            print(f"{progresso} ❌ Fugiu do radar: {nome_filme}")
            
    except Exception as e:
        print(f"{progresso} ⚠️ Erro no filme {nome_filme}: {e}")
        
    time.sleep(0.3) # Respiro pro segurança do TMDB não banir a gente

print("\n3. Fechando a conta e passando a régua... 🧾")
if dados_finais:
    df_resultado = pd.DataFrame(dados_finais)
    df_resultado.to_csv("base_treino_mvp_v1.csv", index=False, sep=";", encoding='utf-8-sig')
    print("TUDO NOSSO! Arquivo 'base_treino_mvp_v1.csv' gerado completão! 🏆")