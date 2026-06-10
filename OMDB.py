import os
import requests
from dotenv import load_dotenv # type: ignore

# 1. Carrega as chaves do cofre
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def buscar_nota_critica(titulo):
    """Busca a nota do Rotten Tomatoes no OMDB com chave protegida."""
    if not OMDB_API_KEY:
        print("❌ Erro: OMDB_API_KEY não encontrada no arquivo .env!")
        return 0
        
    url = f"http://www.omdbapi.com/?t={titulo}&apikey={OMDB_API_KEY}"
    
    try:
        resp = requests.get(url).json()
        ratings = resp.get('Ratings', [])
        
        # Procura especificamente pela nota do Rotten Tomatoes
        for r in ratings:
            if r['Source'] == 'Rotten Tomatoes':
                # Remove o '%' e converte pra inteiro
                return int(r['Value'].replace('%', ''))
        
        return 0 # Retorna 0 se não encontrar o filme ou a nota
    except Exception as e:
        print(f"Deu ruim ao buscar nota do filme '{titulo}': {e}")
        return 0

# --- TESTE À VERA ---
nome_filme = "The Batman"
nota = buscar_nota_critica(nome_filme)
print(f"Nota Rotten Tomatoes de '{nome_filme}': {nota}%")