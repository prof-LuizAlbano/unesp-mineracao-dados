import requests
import re
from bs4 import BeautifulSoup
import sqlite3
from datetime import date

"""
Config vars
"""

# Start page
start_page = 32

# Amount of pages
pages_total = 32

# Amount of items (papers)
pages_items = 50

# Database connection
conn = None

# Databse file
db_file = "dataset/scielo.papers.carbono.db"

"""
Open a connection to a SQLite database file.
"""
def database_connect(database_file):
    global conn
    try:
        with sqlite3.connect(database_file) as conn:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
    except sqlite3.OperationalError as err:
        print("Failed to open database: ", database_file, err)
        exit()


"""
Configura a URL de busca na plataforma SciELO.

:param page: Número da página a ser carregada
:param count: Quantidade de itens carregados
:return: retorna a URL formatada
"""
def parse_url_scielo(page=0, count=50):
    from_count = 0 if page == 1 else (page * count) - 49
    #return f"https://search.scielo.org/?q=*&lang=pt&count={count}&from={from_count}&output=site&sort=&format=summary&fb=&page={page}&filter%5Bin%5D%5B%5D=scl&filter%5Bla%5D%5B%5D=pt&filter%5Bsubject_area%5D%5B%5D=Exact+and+Earth+Sciences&filter%5Btype%5D%5B%5D=research-article"
    return f"https://search.scielo.org/?q=cr%C3%A9dito+de+carbono&lang=pt&count={count}&from={from_count}&output=site&sort=&format=summary&fb=&page={page}&filter%5Bin%5D%5B%5D=scl&filter%5Bla%5D%5B%5D=pt&filter%5Btype%5D%5B%5D=research-article&q=carbono&lang=pt"


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
        return None


"""
ParsePagePaper REESCREVER
"""
def ParsePagePaper(paper_url):
    response = load_site(paper_url)

    if response is None :
        return None

    page = BeautifulSoup(response.text, 'html.parser')

    paper = page.find("div", class_="articleTxt")

    title = paper.find("h1", class_="article-title").text.replace("\n", "") if paper.find("h1", class_="article-title") else ""
    title = str(title) if type(title) == list else title
    subtitle = paper.find("h2", class_="article-title").text.replace("\n", "") if paper.find("h2", class_="article-title") else ""
    subtitle = str(subtitle) if type(subtitle) == list else subtitle
    
    edition_txt = paper.find("span", class_="_editionMeta").text.replace("\n", "")
    edition_txt = re.sub(' +', ' ', edition_txt).split(' • ')
    
    doi = paper.find("a", class_="_doi")

    paper_text = paper.find('div', attrs={'data-anchor': 'Text'}).text

    if paper.find('div', attrs={'data-anchor': 'Text'}) == None :
        return None
    
    paper_text = paper_text.replace("\n", "  ")
    paper_text = paper_text.replace(" [Crossref]Crossref... ", "")
    paper_text = paper_text.replace("[Link]", "")
    paper_text = re.sub(' +', ' ', paper_text)

    return {
        "Title" : str(title),
        "Subtitle" : subtitle,
        "Edition" : edition_txt[0],
        "Paper_Year" : edition_txt[1],
        "DOI" : doi['href'],
        'Content' : paper_text
    }

"""
ParsePageIndex
"""
def parsePageIndex(response):
    global conn

    page = BeautifulSoup(response.text, 'html.parser')
    items = page.select("div.results > div.item")
    
    for item in items :
        url = item.select("div.line a")
        
        authors = item.select("div.line.authors")
        authors = re.sub(' +', '', authors[0].text.replace("\n", "")).replace(";", "; ")

        paper = ParsePagePaper( url[0]['href'] )

        if paper is None:
            continue

        paper['Authors'] = authors
        paper['URL'] = url[0]['href']
        paper['PubDate'] = "2024-11-10"
        paper['Language'] = "pt"

        columns = ', '.join(paper.keys())
        placeholders = ', '.join('?' * len(paper))
        query = "INSERT INTO papers ({}) VALUES ({})".format(columns, placeholders)

        conn.execute(query, tuple(paper.values()))
        conn.commit()


"""
Bootstrap section
"""

database_connect(db_file)

for page in range(start_page, pages_total+1):
    url = parse_url_scielo(page, pages_items)
    res = load_site(url)

    if res is not None:
        parsePageIndex(res)


conn.close()
