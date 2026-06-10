import os
from dotenv import load_dotenv # type: ignore
from transformers import pipeline # type: ignore

print("1. Abrindo o cofre e puxando as credenciais...")
# Carrega as variáveis que estão escondidas no teu arquivo .env
load_dotenv() 

# Puxa a chave específica do Hugging Face
minha_chave_hf = os.getenv("HF_API_KEY")

if not minha_chave_hf:
    print("❌ Deu ruim, cria! Não achei a HF_API_KEY no arquivo .env.")
else:
    # A biblioteca transformers exige que a variável de ambiente se chame HF_TOKEN
    os.environ["HF_TOKEN"] = minha_chave_hf
    print("✅ Autenticação blindada com sucesso!")
    
    print("\n2. Ligando o cérebro do analista de sentimentos...")
    # Agora ele roda 100% autenticado e sem aquele aviso vermelho chato
    analisador = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

    # --- TESTANDO À VERA ---
    comentarios_reddit = [
        "Cara, o trailer tá muito foda, Nolan não erra nunca! Obra prima.",
        "CGI cagado demais, estragaram a franquia. Vou nem gastar dinheiro com ingresso.",
        "Filme ok, nada demais. Roteiro meio fraco mas dá pra passar o tempo.",
        "Melhor filme da minha vida, assistiria umas 10x novamente...",
        "Quero minhas 2h de vida de volta, quer merda de filme"
    ]

    print("\n--- RESULTADOS DA NLP ---")
    for comentario in comentarios_reddit:
        resultado = analisador(comentario)[0]
        nota = resultado['label'] 
        
        print(f"\nComentário: {comentario}")
        print(f"Veredito da Máquina: {nota}")

print("\n🚀 Script rodou liso e em segurança!")