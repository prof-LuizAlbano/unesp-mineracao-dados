import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

"""
Config vars
"""

# Amount of pages
pages_total = 1 #130

# Amount of items (papers)
pages_items = 50

# Database connection
conn = None

"""
Open a connection to a SQLite database file.
"""
def database_connect(database_file):
    global conn
    try:
        with sqlite3.connect(database_file) as conn:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
    except sqlite3.OperationalError as err:
        print("Failed to open datanase: ", database_file, e)


"""
Configura a URL de busca na plataforma SciELO.

:param page: Número da página a ser carregada
:param count: Quantidade de itens carregados
:return: retorna a URL formatada
"""
def parse_url_scielo(page=0, count=50):
    from_count = 0 if page == 1 else (page * count) - 49
    return f"https://search.scielo.org/?q=*&lang=pt&count={count}&from={from_count}&output=site&sort=&format=summary&fb=&page={page}&filter%5Bin%5D%5B%5D=scl&filter%5Bla%5D%5B%5D=pt&filter%5Bsubject_area%5D%5B%5D=Exact+and+Earth+Sciences&filter%5Btype%5D%5B%5D=research-article"


"""
Função para carregamento do conteúdo das URLs de busca na plataforma SciELO

:param page: Número da página a ser carregada
:param count: Quantidade de itens carregados
:return: retorna um objeto contendo os dados da resposta da requisição
"""
def load_site(url):
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', }
    response = requests.get(url, headers=headers)

    print(f'URL requisitada: {url}')

    if response.status_code == 200 :
        print(f"Sucesso: código de retorno {response.status_code}")
        return response
    else :
        print(f'Falha na requisição - código do erro: {response.status_code}')


"""
ParsePagePaper REESCREVER
"""
def parsePageIndex(response, df):
    page = BeautifulSoup(response.text, 'html.parser')
    items = page.select("div.results > div.item")
    
    for item in items :
        title = item.select("div.line strong.title")
        url = item.select("div.line a")

        df = df._append({ "Title" : title[0].text.strip(), "URL" : url[0]['href']}, ignore_index = True)
    return df

"""
ParsePageIndex
"""
def parsePageIndex(response, df):
    page = BeautifulSoup(response.text, 'html.parser')
    items = page.select("div.results > div.item")
    
    for item in items :
        title = item.select("div.line strong.title")
        url = item.select("div.line a")

        df = df._append({ "Title" : title[0].text.strip(), "URL" : url[0]['href']}, ignore_index = True)
    return df


"""
Bootstrap section
"""

df = pd.DataFrame({ "Title" : [], "URL" : [] })
print(df)

for page in range(1, pages_total+1):
    url = parse_url_scielo(page, pages_items)
    res = load_site(url)
    df = parsePageIndex(res, df)


df.to_excel("Artigos_SciELO.xlsx")



#Colunas: ID, Título, Subtítulo, Palavras-chave, Autores, Resumo, Texto, Ano Publicação, Editors, DOI

# SciELO pages:
# https://www.scielo.br/j/qn/a/XnhMZ3mhrQWRMTbZJRhqtTF/?lang=pt#
# https://search.scielo.org/?q=*&lang=pt&count=50&from=1&output=site&sort=&format=summary&fb=&page=1&filter%5Bin%5D%5B%5D=scl&filter%5Bla%5D%5B%5D=pt&filter%5Bsubject_area%5D%5B%5D=Exact+and+Earth+Sciences&filter%5Btype%5D%5B%5D=research-article
# https://theleftjoin.com/how-to-write-a-pandas-dataframe-to-an-sqlite-table/