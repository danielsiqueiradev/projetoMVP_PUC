import pandas as pd #type: ignore
import glob

# 1. A TUA REGRA DE NEGÓCIO (O DE/PARA BLINDADO)
def padronizar_cinema(nome_sujo):
    nome_upper = str(nome_sujo).upper() # Garante que é texto e tudo maiúsculo
    
    # Adicione os teus cinemas aqui:
    if 'BOULEVARD' in nome_upper:
        return 'KINOPLEX BOULEVARD'
    elif 'D. PEDRO' in nome_upper:
        return 'KINOPLEX DOM PEDRO'
    elif 'TIJUCA' in nome_upper:
        return 'KINOPLEX TIJUCA'
    elif 'VILA OLIMPIA' in nome_upper:
        return 'KINOPLEX VILA OLIMPIA'
    elif 'GRANDE RIO' in nome_upper:
        return 'KINOPLEX GRANDE RIO'
    elif 'ITAIM' in nome_upper:
        return 'KINOPLEX ITAIM'
    elif 'MACEIÓ' in nome_upper:
        return 'KINOPLEX MACEIÓ'
    elif 'PARKSHOPPING' in nome_upper:
        return 'KINOPLEX PARKSHOPPING'
    elif 'PARQUE DA CIDADE' in nome_upper:
        return 'KINOPLEX PARQUE DA CIDADE'
    elif 'RIO SUL' in nome_upper:
        return 'KINOPLEX RIO SUL'
    elif 'VIA PARQUE' in nome_upper:
        return 'KINOPLEX VIA PARQUE'
    elif 'WEST' in nome_upper:
        return 'KINOPLEX WEST SHOPPING'
    elif 'LEBLON GLOBOPLAY' in nome_upper:
        return 'KINOPLEX LEBLON GLOBOPLAY'
    elif 'MADUREIRA' in nome_upper:
        return 'KINOPLEX MADUREIRA'
    elif 'EMPRESA CINEMAS' in nome_upper:
        return 'KINOPLEX GRANDE RIO'
    elif 'GRANDE RIO' in nome_upper:
        return 'KINOPLEX GRANDE RIO'
    elif 'GSR KINOPLEX AMAZ' in nome_upper:
        return 'KINOPLEX AMAZONAS'
    elif 'AVENIDA' in nome_upper:
        return 'KINOPLEX AVENIDA'
    elif 'CARIOCA ME' in nome_upper:
        return 'CINECARIOCA MÉIER'
    elif 'OSASCO' in nome_upper:
        return 'KINOPLEX OSASCO'
    elif 'PRAIA' in nome_upper:
        return 'KINOPLEX PRAIA DA COSTA'
    elif 'SHOPPING BOULEVARD' in nome_upper:
        return 'KINOPLEX SHOPPING BOULEVARD'
    elif 'TOP' in nome_upper:
        return 'KINOPLEX TOP SHOPPING'
    elif 'ODEON' in nome_upper:
        return 'KINOPLEX ODEON'
    elif 'UBERABA' in nome_upper:
        return 'KINOPLEX UBERABA'
    elif 'PR.COSTA' in nome_upper:
        return 'KINOPLEX PRAIA DA COSTA'
    elif 'PR. COSTA' in nome_upper:
        return 'KINOPLEX PRAIA DA COSTA'
    elif 'MALL' in nome_upper:
        return 'KINOPLEX FASHION MALL'
    elif 'MACEIO' in nome_upper:
        return 'KINOPLEX MACEIÓ'
    elif 'AMÉRICA' in nome_upper:
        return 'KINOPLEX NOVA AMÉRICA'
    elif 'VILA OLÍMPIA' in nome_upper:
        return 'KINOPLEX VILA OLÍMPIA' 
    elif 'LEBLON' in nome_upper:
        return 'KINOPLEX LEBLON'
    elif 'AMAZONAS' in nome_upper:
        return 'KINOPLEX AMAZONAS'   
    elif 'MACEIÃ“' in nome_upper:
        return 'KINOPLEX MACEIÓ'
    elif 'IMAX KINOPLEX DOM PEDRO' in nome_upper:
        return 'KINOPLEX DOM PEDRO'
    elif 'GOLDEN' in nome_upper:
        return 'KINOPLEX GOLDEN'
    elif 'IGUAÇU' in nome_upper:
        return 'KINOPLEX NOVA IGUAÇU'
    elif 'IGUACU' in nome_upper:
        return 'KINOPLEX NOVA IGUAÇU' 
    elif 'VILA OLÍMPIA' in nome_upper:
        return 'KINOPLEX VILA OLÍMPIA'
      

    else:
        # Se passar batido, ele devolve o nome original pra tu caçar depois
        return nome_upper 

# 2. LENDO OS ARQUIVOS DA ANCINE
arquivos_csv = glob.glob("bilheteria-diaria-obras-por-distribuidoras-csv/*.csv")
lista_de_dados = []

for arquivo in arquivos_csv:
    print(f'Lendo arquivo csv: {arquivo}')
    dados = pd.read_csv(arquivo, sep=';', encoding='utf-8', low_memory=False)
    lista_de_dados.append(dados)

tabela_completa = pd.concat(lista_de_dados, ignore_index=True)

# 3. FILTROS BOLADOS
filtro_kinoplex = tabela_completa['NOME_SALA'].str.contains('KINOPLEX', case=False, na=False)
filtro_uci = ~tabela_completa['NOME_SALA'].str.contains('UCI', case=False, na=False)
filtro_vale = ~tabela_completa['NOME_SALA'].str.contains('VALE', case=False, na=False)

tabela_filtrada = tabela_completa[(filtro_kinoplex) & (filtro_uci) & (filtro_vale)].copy()

# 4. APLICANDO O TEU MAPEAMENTO
print('Padronizando os nomes dos cinemas...')
tabela_filtrada['NOME_CINEMA'] = tabela_filtrada['NOME_SALA'].apply(padronizar_cinema)

# 5. TRATANDO AS DATAS
tabela_filtrada['DATA_EXIBICAO'] = pd.to_datetime(tabela_filtrada['DATA_EXIBICAO'], dayfirst=True, errors='coerce')
tabela_filtrada['MES_EXIBICAO'] = tabela_filtrada['DATA_EXIBICAO'].dt.month
tabela_filtrada['ANO_EXIBICAO'] = tabela_filtrada['DATA_EXIBICAO'].dt.year

# 6. ENXUGANDO A BASE
colunas_filtradas = ['MES_EXIBICAO', 'ANO_EXIBICAO', 'TITULO_ORIGINAL', 'NOME_CINEMA', 'PUBLICO']
tabela_enxuta = tabela_filtrada[colunas_filtradas]

# 7. AGRUPANDO E SOMANDO O FATURAMENTO
print('Consolidando o público...')
tabela_agrupada = tabela_enxuta.groupby(['MES_EXIBICAO', 'ANO_EXIBICAO', 'NOME_CINEMA', 'TITULO_ORIGINAL']).agg({
    'PUBLICO': 'sum'
}).reset_index()
# 8. FORÇANDO TUDO QUE É TEXTO A FICAR MAIÚSCULO E SEM ESPAÇOS INÚTEIS NAS PONTAS.
tabela_agrupada['NOME_CINEMA'] = tabela_agrupada['NOME_CINEMA'].str.upper().str.strip()
tabela_agrupada['TITULO_ORIGINAL'] = tabela_agrupada['TITULO_ORIGINAL'].astype(str).str.upper().str.strip()

# 9. SALVANDO A BASE DE OURO
tabela_agrupada.to_csv('Resultado_Kinoplex_Por_Complexo.csv', index=False, sep=';', encoding='utf-8-sig')
print('Ai sim, rodou liso! Base consolidada com sucesso!')