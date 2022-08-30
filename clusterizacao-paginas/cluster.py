#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('pip install jellyfish')
get_ipython().system('pip install html-similarity')


# In[1]:


import urllib3
import jellyfish
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib3.exceptions import *
from html_similarity import style_similarity, structural_similarity, similarity

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-web-security")
options.add_argument('--headless')


# In[2]:


paginas_base = ["https://freigaspar.mg.gov.br/transparencia/empenhos", 
                "https://freigaspar.mg.gov.br/transparencia/pagamentos",
                "https://freigaspar.mg.gov.br/transparencia/receitas"]

coletor_1 = ["https://freigaspar.mg.gov.br/transparencia/folhas-de-pagamento/detalhes?indSituacaoServidorPensionista%5B0%5D=P&indSituacaoServidorPensionista%5B1%5D=03&IDE_FLPGO_id=35&ano=2015",
             "https://freigaspar.mg.gov.br/transparencia/empenhos/detalhes/2022/02/118",
             "https://freigaspar.mg.gov.br/transparencia/pagamentos/detalhes/2022/02/118"]

coletor_2 = ["https://freigaspar.mg.gov.br/transparencia/empenhos/exibir/2022/02/33089",
             "https://freigaspar.mg.gov.br/transparencia/pagamentos/exibir/2021/12/35798",
             "https://freigaspar.mg.gov.br/transparencia/empenhos/exibir/2022/05/34915"]

paginas_extras = ["https://freigaspar.mg.gov.br/transparencia",
                  "https://freigaspar.mg.gov.br/transparencia/folhas-de-pagamento",
                  "https://freigaspar.mg.gov.br/transparencia/coronavirus"]

testes = paginas_base + coletor_1 + coletor_2 + paginas_extras


# ## Jellyfish

# In[5]:


def extrairHtml(url):

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        soup = BeautifulSoup(driver.page_source, "lxml")
        
        driver.close()
        
        for elm in soup.find_all():
            if not elm.find(recursive=False):
                elm.string = ''
            elm.attrs = {}
            
        html = str(soup.prettify()).replace("\n", "")
            
        return html.replace(" ", "")

    
    except:
        driver.close()
        
        print("Erro ao tentar abrir a pagina: " + url)


# In[6]:


extrairHtml("https://freigaspar.mg.gov.br/transparencia/coronavirus")


# In[7]:


testes_1 = [extrairHtml(teste) for teste in testes]


# In[8]:


for page in testes_1:
    for page_aux in testes_1:
        print(f"{jellyfish.jaro_distance(page,page_aux):.2f}", end = " ")
    print("\n")


# In[9]:


for page in testes_1:
    for page_aux in testes_1:
        print(f"{jellyfish.hamming_distance(page,page_aux):.2f}", end = " ")
    print("\n")


# In[13]:


for page in testes_1:
    for page_aux in testes_1:
        print(f"{jellyfish.jaro_winkler(page,page_aux):.2f}", end = " ")
    print("\n")


# ## HTML similarity

# In[14]:


for page in testes_1:
    for page_aux in testes_1:
        print(f"{structural_similarity(page,page_aux):.2f}", end = " ")
    print("\n")


# In[15]:


for page in testes_1:
    for page_aux in testes_1:
        print(f"{similarity(page,page_aux):.2f}", end = " ")
    print("\n")


# In[16]:


def extrairHtmlCompleto(url):

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        soup = BeautifulSoup(driver.page_source, "lxml")
        driver.close()
        
        html = str(soup)
            
        return html
    
    except:
        driver.close()
        print("Erro ao tentar abrir a pagina: " + url)


# In[17]:


testes_2 = [extrairHtmlCompleto(teste) for teste in testes]


# In[18]:


for page in testes_2:
    for page_aux in testes_2:
        print(f"{structural_similarity(page,page_aux):.2f}", end = " ")
    print("\n")


# In[19]:


for page in testes_2:
    for page_aux in testes_2:
        print(f"{style_similarity(page,page_aux):.2f}", end = " ")
    print("\n")


# In[20]:


for page in testes_2:
    for page_aux in testes_2:
        print(f"{similarity(page,page_aux):.2f}", end = " ")
    print("\n")


# ## Extração de botões??

# In[21]:


def extrairBotoes(url):

    resultados = ""
    
    page = requests.get(url)
    data = page.text
    soup = BeautifulSoup(data, 'html.parser')
    
    buttons = soup.find_all('button')
    for button in buttons:
        resultados+=str(button) + "\n"
        
    return resultados


# In[22]:


testes_3 = [extrairBotoes(teste) for teste in testes]


# In[23]:


for page in testes_3:
    for page_aux in testes_3:
        print(f"{similarity(page,page_aux):.2f}", end = " ")
    print("\n")


# In[24]:


def extrairBotoesSelenium(url):

    resultados = ""

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')
    buttons = soup.find_all('button')
    for button in buttons:
        resultados+=str(button)+"\n"
        
    return resultados


# In[16]:


empenhos = extrairBotoesSelenium("https://freigaspar.mg.gov.br/transparencia/empenhos")
empenhos2 = extrairBotoesSelenium("https://freigaspar.mg.gov.br/transparencia/empenhos/detalhes/2022/02/118")
pagamentos = extrairBotoesSelenium("https://freigaspar.mg.gov.br/transparencia/pagamentos")
pagamentos2 = extrairBotoesSelenium("https://freigaspar.mg.gov.br/transparencia/pagamentos/detalhes/2022/02/118")
folhas = extrairBotoesSelenium("https://freigaspar.mg.gov.br/transparencia/folhas-de-pagamento")
folhas2 = extrairBotoesSelenium("https://freigaspar.mg.gov.br/transparencia/folhas-de-pagamento/detalhes?indSituacaoServidorPensionista%5B0%5D=P&indSituacaoServidorPensionista%5B1%5D=03&IDE_FLPGO_id=35&ano=2015")
receitas = extrairBotoesSelenium("https://freigaspar.mg.gov.br/transparencia/receitas/detalhes/2022/03/117")

pages = [empenhos, empenhos2, pagamentos, pagamentos2, folhas, folhas2, receitas]


# In[25]:


testes_4 = [extrairBotoesSelenium(teste) for teste in testes]


# In[26]:


for page in testes_4:
    for page_aux in testes_4:
        print(f"{similarity(page,page_aux):.2f}", end = " ")
    print("\n")


# In[ ]:




