#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
import os
import time
import urllib3
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# In[2]:


cidades = ['Novo Oriente de Minas',
     'Frei Gaspar',
     'Fronteira dos Vales',
     'Chapada do Norte',
     'Sardoá',
     'Bertópolis',
     'Cuparaque',
     'Coroaci',
     'Machacalis',
     'Periquito',
     'Itabirinha',
     'São Sebastião do Maranhão',
     'Caraí',
     'Ataléia',
     'Ouro Verde de Minas',
     'Itaipé',
     'Umburatiba',
     'Marilac',
     'Jordânia',
     'São João Evangelista',
     'Bandeira',
     'Tumiritinga',
     'Santa Efigênia de Minas',
     'Pavão',
     'Pescador',
     'Cantagalo',
     'Santo Antônio do Jacinto']

tags = ["licitacoes", "contratos", "empenhos", "receitas", "folhas-de-pagamento", "pagamentos", "diarias", "obras", "relatorios"]
subpastas = ["screenshots", "files", "htmls"]

cidades_urls = {'Novo Oriente de Minas': ["https://novoorientedeminas.mg.gov.br/transparencia", "https://no"],
     'Frei Gaspar': ["https://freigaspar.mg.gov.br/transparencia", "https://www.fr"],
     'Fronteira dos Vales': ["https://fronteiradosvales.mg.gov.br/transparencia", "https://fr"],
     'Chapada do Norte': ["https://chapadadonorte.mg.gov.br/transparencia", "https://ch"],
     'Sardoá': ["https://sardoa.mg.gov.br/transparencia", "https://sa"],
     'Bertópolis': ["https://bertopolis.mg.gov.br/transparencia", "https://be"],
     'Cuparaque': ["https://cuparaque.mg.gov.br/transparencia", "https://cu"],
     'Coroaci': ["https://coroaci.mg.gov.br/transparencia", "https://co"],
     'Machacalis': ["https://machacalis.mg.gov.br/transparencia", "https://ma"],
      #'Periquito':
     'Itabirinha': ["https://itabirinha.mg.gov.br/transparencia", "https://it"],
     'São Sebastião do Maranhão': ["https://saosebastiaodomaranhao.mg.gov.br/transparencia", "https://sa"],
     'Caraí': ["https://carai.mg.gov.br/transparencia", "https://ca"],
     'Ataléia': ["https://ataleia.mg.gov.br/transparencia", "https://at"],
     'Ouro Verde de Minas': ["https://ouroverdedeminas.mg.gov.br/transparencia", "https://ou"],
     'Itaipé': ["https://itaipe.mg.gov.br/transparencia", "https://it"],
     'Umburatiba': ["https://umburatiba.mg.gov.br/transparencia", "https://um"],
     'Marilac': ["https://marilac.mg.gov.br/transparencia", "https://ma"],
     'Jordânia': ["https://jordania.mg.gov.br/transparencia", "https://jo"],
     'São João Evangelista': ["https://sje.mg.gov.br/transparencia", "https://sj"],
     'Bandeira': ["https://bandeira.mg.gov.br/transparencia", "https://ba"],
     'Tumiritinga': ["https://tumiritinga.mg.gov.br/transparencia", "https://tu"],
     'Santa Efigênia de Minas': ["https://santaefigenia.mg.gov.br/transparencia", "https://sa"],
     'Pavão': ["https://pavao.mg.gov.br/transparencia", "https://pa"],
     'Pescador': ["https://pescador.mg.gov.br/transparencia", "https://pe"],
     'Cantagalo': ["https://cantagalo.mg.gov.br/transparencia", "https://ca"],
     'Santo Antônio do Jacinto': ["https://www.santoantoniodojacinto.mg.gov.br/transparencia", "https://www.sa"]}


# In[3]:


def create_pastes():

    try:
        os.mkdir("C:\\Users\\Arthur\\Desktop\\template2")
    except FileExistsError:
        pass

    for cidade in cidades:
        try:
            os.mkdir("C:\\Users\\Arthur\\Desktop\\template2\\" + cidade)
            for tag in tags:
                os.mkdir("C:\\Users\\Arthur\\Desktop\\template2\\" + cidade + "/" + tag)
                for sub in subpastas:
                    os.mkdir("C:\\Users\\Arthur\\Desktop\\template2\\" + cidade + "/" + tag + "/" + sub)
        except FileExistsError:
            continue


# In[4]:


def coletor_unico(cidade, tag, url):

    try:
    
        options = webdriver.ChromeOptions() 
        options.add_argument('--headless')
        options.add_argument("--start-maximized")
        prefs = {"profile.default_content_settings.popups": 0,
                     "download.default_directory": 
                                "C:\\Users\\Arthur\\Desktop\\template2\\"+cidade+"\\"+tag+"\\files\\",#IMPORTANT - ENDING SLASH V IMPORTANT
                     "directory_upgrade": True}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=options)

        driver.get(url)
        time.sleep(3)
        driver.save_screenshot("C:\\Users\\Arthur\\Desktop\\template2\\" + cidade + "\\" + tag + "\\screenshots\\" + tag + ".png")
        driver.find_element(By.XPATH, "/html/body/div[8]/div[2]/main/section/div/div/div/div/div/div[2]/div[1]/button[3]/span").click()
        time.sleep(3)

        driver.close()
        
    except:
        print("Erro ao baixar: " + "\"" + tag + "\"" + " na url " + url)


# In[5]:


def crawl(pages, depth, tags, restriction):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    already_visited = set(pages)
    
    dic = {}
    for tag in tags:
        dic[tag] = []

    for i in range(depth):
        new_pages = set()
        print("Actual depth: " + str(i))

        for page in pages:
            http = urllib3.PoolManager()
            try:
                page_data = http.request('GET', page)
            except:
                print("Error: " + page)
                continue


            soup = BeautifulSoup(page_data.data, "lxml")
            #text = getText(soup)
            already_visited.add(page)

            links = soup.find_all('a')
            counter = 0

            for link in links:

                if("href" in link.attrs):
                    url = urljoin(page, str(link.get('href')))

                    if url.find("'") != -1:
                        continue

                    url = url.split("#")[0]

                #Restriction to prevent the crawler get out the base url - Especific for Template2 - Frei Gaspar
                if url.startswith(restriction):
                    new_pages.add(url)
                    for tag in tags:
                        if tag in url and "detalhes" in url:
                            dic[tag].append(url)

            counter += 1

        pages = new_pages.difference(already_visited)

        print("Number of links visited: " +  str(len(already_visited)))

    return dic


# In[6]:


def colect(cidade, url, restriction):
    
    links = crawl([url], 2, tags, restriction)
    
    for key, value in links.items():
        for link in value:
            coletor_unico(cidade, key, link)
    
    print("Relatorio de coleta da cidade " + "\"" + cidade + "\"")
    for subtag in os.listdir("C:\\Users\\Arthur\\Desktop\\template2\\"+ cidade):
        print("Coletado " + str(len("C:\\Users\\Arthur\\Desktop\\template2\\" + cidade + "\\" + subtag + "\\files")) + 
              " documentos na subtag " + subtag)


# In[ ]:


create_pastes()

for key, value in cidades_urls.items():
    colect(key, value[0], value[1])


# In[ ]:




