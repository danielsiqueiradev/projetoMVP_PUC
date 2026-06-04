import pandas as pd

print("Iniciando a união das bases de dados...")

# 1. Carregando as bases geradas na etapa anterior
df_faturamento = pd.read_csv('Resultado_Kinoplex_5k_Mais.csv', sep=';', encoding='utf-8')
df_tmdb = pd.read_csv('Base_TMDB_Filmes.csv', sep=';', encoding='utf-8')

# 2. Realizando o cruzamento (Merge)
# Utilizamos 'left' para garantir que a base de faturamento dita as regras
df_final = pd.merge(df_faturamento, df_tmdb, on='TITULO_ORIGINAL', how='left')

# 3. Tratamento de dados ausentes 
# Caso a API não tenha encontrado informações de algum filme específico
df_final.fillna('Desconhecido', inplace=True)

# 4. Salvando a base consolidada para o treinamento do modelo preditivo
df_final.to_csv('Base_Kinoplex_ML_Pronta.csv', index=False, sep=';', encoding='utf-8-sig')

print("Operação concluída. O arquivo 'Base_Kinoplex_ML_Pronta.csv' foi gerado com sucesso e está pronto para o algoritmo.")