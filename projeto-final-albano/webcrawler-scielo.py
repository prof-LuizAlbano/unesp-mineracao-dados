import requests
import re
from bs4 import BeautifulSoup
import pandas as pd


"""
Função para carregamento do conteúdo das URLs de busca na plataforma SciELO

:param page: Número da página a ser carregada
:param count: Quantidade de itens carregados
:return: retorna um objeto contendo os dados da resposta da requisição
"""
def load_site(page=0, count=50):
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', }

    from_count = 0 if page == 1 else (page * count) - 49
    link = f"https://search.scielo.org/?q=*&lang=pt&count={count}&from={from_count}&output=site&sort=&format=summary&fb=&page={page}&filter%5Bin%5D%5B%5D=scl&filter%5Bla%5D%5B%5D=pt&filter%5Bsubject_area%5D%5B%5D=Exact+and+Earth+Sciences&filter%5Btype%5D%5B%5D=research-article"

    response = requests.get(link, headers=headers)

    print(f'URL requisitada: {link}')

    if response.status_code == 200 :
        print(f"Sucesso: código de retorno {response.status_code}")
        return response
    else :
        print(f'Falha na requisição - código do erro: {response.status_code}')


def parsePage(response, df):
    page = BeautifulSoup(response.text, 'html.parser')
    #results = page.find("div", class_="results")
    items = page.select("div.results > div.item")
    
    for item in items :
        title = item.select("div.line strong.title")
        url = item.select("div.line a")

        df = df._append({ "Title" : title[0].text.strip(), "URL" : url[0]['href']}, ignore_index = True)
    return df


pages_total = 130
pages_itens = 50

df = pd.DataFrame({ "Title" : [], "URL" : [] })
print(df)

for page in range(1, pages_total+1):
    res = load_site(page, pages_itens)
    df = parsePage(res, df)


df.to_excel("Artigos_SciELO.xlsx")