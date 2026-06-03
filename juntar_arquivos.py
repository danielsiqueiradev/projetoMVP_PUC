import pandas as pd #type: ignore
import glob

arquivos_csv = glob.glob("bilheteria-diaria-obras-por-distribuidoras-csv/*.csv")
lista_de_dados = []

for arquivo in arquivos_csv:
    print(f'Lendo arquivo csv{arquivo}')

    dados = pd.read_csv(arquivo, sep=';', encoding='latin1', low_memory=False)
    lista_de_dados.append(dados)

tabela_completa = pd.concat(lista_de_dados, ignore_index=True)
filtro_kinoplex = tabela_completa['NOME_SALA'].str.contains('KINOPLEX', case=False, na=False)
filtro_uci = ~tabela_completa['NOME_SALA'].str.contains('UCI', case=False, na=False)
filtro_vale = ~tabela_completa['NOME_SALA'].str.contains('VALE', case=False, na=False)
tabela_filtrada = tabela_completa[(filtro_kinoplex)&(filtro_uci)&(filtro_vale)]
colunas_filtradas = ['TITULO_ORIGINAL','NOME_SALA', 'PUBLICO']
tabela_enxuta = tabela_filtrada[colunas_filtradas]

tabela_agrupada = tabela_enxuta.groupby(['NOME_SALA', 'TITULO_ORIGINAL']).agg({
    'PUBLICO': 'sum'
}).reset_index()

tabela_agrupada.to_csv('Resultado_Kinoplex_Consolidado.csv', index=False, sep=';', encoding='latin1')
print('Funcionou!')