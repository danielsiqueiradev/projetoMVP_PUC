import pandas as pd

def desembolar_texto(texto):
    """Malandragem pra desfazer a confusão de acentos (Mojibake)"""
    if isinstance(texto, str):
        try:
            # Pega a string bugada e força a leitura correta
            return texto.encode('latin1').decode('utf-8')
        except:
            return texto
    return texto

def binarizar_tudo_limpo():
    print("🛠️ Iniciando a Binarização da Base (Agora com desinfetante)...")
    
    # Lendo o arquivo original
    df = pd.read_csv("Base_Kinoplex_ML_Final_Patched.csv")
    
    # Tirando aquele lixo 'ï»¿' que fica no começo da primeira coluna às vezes
    df.rename(columns=lambda x: x.replace('ï»¿', ''), inplace=True)
    
    # ==========================================
    # 0. A FAXINA ANTES DA MÁGICA
    # ==========================================
    print("🧽 Limpando os nomes zoados e acentos quebrados...")
    colunas_pra_limpar = ['GENEROS', 'NOME_CINEMA', 'TITULO_ORIGINAL']
    for col in colunas_pra_limpar:
        if col in df.columns:
            df[col] = df[col].apply(desembolar_texto)

    # ==========================================
    # 1. BINARIZANDO OS GÊNEROS 
    # ==========================================
    print("🎬 Fatiando a coluna de Gêneros...")
    df['GENEROS'] = df['GENEROS'].fillna('Desconhecido') 
    
    generos_dummies = df['GENEROS'].str.get_dummies(sep=', ')
    generos_dummies.columns = ['GENERO_' + col for col in generos_dummies.columns]
    
    # ==========================================
    # 2. BINARIZANDO CINEMA E CLASSIFICAÇÃO
    # ==========================================
    print("🍿 Binarizando Cinemas e Classificação Indicativa...")
    df_dummies = pd.get_dummies(df, columns=['CLASSIFICACAO', 'NOME_CINEMA'], prefix=['CLASS', 'CINEMA'])
    
    # ==========================================
    # 3. JUNTANDO TUDO NO MESMO BOLADÃO
    # ==========================================
    print("🧱 Juntando os blocos...")
    df_final = pd.concat([df_dummies, generos_dummies], axis=1)
    df_final = df_final.drop('GENEROS', axis=1)
    
    # Convertendo os booleanos (True/False) pra 1 e 0 pra ficar no padrão numérico
    for col in df_final.columns:
        if df_final[col].dtype == 'bool':
            df_final[col] = df_final[col].astype(int)
    
    # Salvando com utf-8-sig pra não bugar NUNCA MAIS se tu abrir no Excel
    nome_arquivo_final = "Base_Kinoplex_ML_Binarizada.csv"
    df_final.to_csv(nome_arquivo_final, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ VRAU! Binarização Concluída!")
    print(f"O arquivo {nome_arquivo_final} tá limpinho, com os nomes corretos e pronto pro ML!")

if __name__ == "__main__":
    binarizar_tudo_limpo()