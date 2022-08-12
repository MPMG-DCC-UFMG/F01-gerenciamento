#!/usr/bin/env python
# coding: utf-8

# In[33]:


get_ipython().system('pip install ahocorapy')
get_ipython().system('pip install lxml')


# In[1]:


import urllib3
import pandas as pd
import numpy as np
from time import sleep

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ahocorapy.keywordtree import KeywordTree

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-web-security")
options.add_argument("--headless")
prefs = {"download_restrictions": 3}
options.add_experimental_option("prefs", prefs)


# In[2]:


def getText(html):

    for tags in html(['script', 'style']):
        tags.decompose

    return ' '. join(html.stripped_strings)


# In[3]:


def findPatterns(text, tree, page, df, cidade):

    results = kwtree.search_all(text)
    results = [result[0] for result in results]
    results_unique = set(results)

    for result in results_unique:
    #if results.count(result) > 1: #para exigir que resultados so sejam validos se ocorrerem mais de uma vez na pagina
        print("\"" + result + "\" found " + str(results.count(result)) + " time(s) on page: " + page)
        df.loc[cidade][result] = True
    
    df.to_csv("resultados_intermediarios.csv")

    if len(results) != 0:
        print("\n")


# In[4]:


def crawl(pages, depth, kwtree, df, cidade, restrictions, url_complement = ""):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    already_visited = set(pages)

    for i in range(depth):
        new_pages = set()
        print("Actual depth: " + str(i))

        for page in pages:
            
            driver = webdriver.Chrome(options=options)
            driver.get(page)
            
            #GRP necessita de maior tempo para renderização da pagina
            #if df_templates.loc[cidade]["Template"] == "GRP":
            #    sleep(2)
            
            try:
                soup = BeautifulSoup(driver.page_source)
                text = getText(soup)
                driver.close()
                
            except:
                print("Error: " + page)
                continue


            findPatterns(text, kwtree, page, df, cidade)
            already_visited.add(page)

            links = soup.find_all('a')
            counter = 0

            for link in links:
                url = ""

                if("href" in link.attrs):
                    url = urljoin(page, str(link.get('href')))

                if url.find("'") != -1:
                    continue

                # GRP so possui links com #. Entretanto, mesmo sem o split 
                #desse caracter esses links nao sao gerados   
                #if df_templates.loc[cidade]["Template"] != "GRP":
                url = url.split("#")[0]

                is_valid = False

                #Restriction to prevent the crawler get out the base url
                for rst in restrictions[0]:
                    if url.startswith(rst):
                        is_valid = True

                for rst in restrictions[1]:
                    if rst in url:
                        is_valid = False
                        break

                if is_valid:
                    new_pages.add(url + url_complement)

                counter += 1

            pages = new_pages.difference(already_visited)
            
        print("Number of links visited: " +  str(len(already_visited)))


# In[5]:


kwtree = KeywordTree(case_insensitive=True)

#tags = ["Plano Plurianual", "Auxílios", "Aposentadoria", "Pensão", "Parceria", "Repasse", "Conselho", "Lei de Diretrizes", "Fiscal", "Viagens", "Resumido", "Modalidade", "Folha Pagamento", "Liquidado", "Planejamento", "Fatura", "Consolidado", "Previsto", "Arrecadado", "Concurso", "Vigencia", "Pregão Presencial", "Relatórios", "Servidores", "Obra", "Meta"]
#tags = ["Concurso","Plano", "Metas", "Terceiro setor", "Repasse", "Servidor", "Parceria"]
#tags = ["12.527/2011", "45.969/2012", "www.transparencia.mg.gov.br", " Lei de Acesso à Informação", "CODEMA", "CMDCA"]
tags = ["Transparência", "12.527/2011", "45.969/2012", "www.transparencia.mg.gov.br", "Lei de Acesso à Informação", "Conselho", "CODEMA", "CMDCA", "F.A.Q", "FAQ", "Perguntas Frequentes", "Pedidos", "Estrutura Organizacional", "Endereço", "Telefone", "Horário de Atendimento", "Conselhos Municipais", "Receitas", "Consolidado", "Liquida", "Previs", "Arrecada", "Classificação","Balanço", "Contas", "Meta", "Plano de Metas", "Gestão fiscal", "Resumido de Execução", "Diretrizes", "Orçament",  "Pagamentos", "Pagar", "Empenhos", "N° de empenho", "N° do empenho", "Valor", "Favorecido", "Licitaç", "Status", "Modalidade", "Resultado", "Status","Contrato", "Vigência", "Terceiro Setor", "Parcerias", "Repasses", "Data de celebração", "Data", "Conveniado", "Origem", "Recurso", "Concurso", "Conselho", "Pensão", "Plano Plurianual", "Concurso Público", "Obra", "Situação", "Servidor", "Nome", "Cargo", "Função", "Relatorio Mensal", "Despesa com Pessoal", "Despesas com pessoal", "Aposentado", "Pensionista", "Diária", "Viagen", "Viagem", "Periodo", "Convênios", "Destino", "Motivo", "Prestação", "Repasse", "Legisl"]

for tag in tags:
    kwtree.add(tag)
kwtree.finalize()


# ## Busca Templates

# In[53]:


#pd.set_option('max_columns', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

cidades_dic = {#Template2
               "Frei Gaspar": ["https://freigaspar.mg.gov.br/transparencia",["https://fr"], ["detalhes", "noticias"],""],
               "Coroaci": ["https://coroaci.mg.gov.br/transparencia",["https://co"], ["detalhes", "noticias"],""],
               "Machacalis": ["https://machacalis.mg.gov.br/transparencia",["https://ma"], ["detalhes", "noticias"],""],
               "Sardoá": ["https://sardoa.mg.gov.br/transparencia",["https://sa"], ["detalhes", "noticias"],""],
               "Cuparaque": ["https://cuparaque.mg.gov.br/transparencia",["https://cu"], ["detalhes", "noticias"],""],
               #Portal TP
               "Abre Campo": ["https://abrecampo-mg.portaltp.com.br/", ["https://ab"], ["consultas"],""],
               "Manhuaçu": ["https://manhuacu-mg.portaltp.com.br/", ["https://ma"], ["consultas"],""],
               "São Geraldo do Baixio": ["https://saogeraldodobaixio-mg.portaltp.com.br/", ["https://sa"], ["consultas"],""],
               "Almenara": ["https://almenara-mg.portaltp.com.br/", ["https://al"], ["consultas"],""],
               "João Monlevade": ["https://portaltransparenciajm.portaltp.com.br/", ["https://por"], ["consultas"],""],
               #Siplanweb
               "Aracitaba": ["https://pm-aracitaba.publicacao.siplanweb.com.br/",["https://pm-"], [],""], 
               "Cruzília": ["https://pm-cruzilia.publicacao.siplanweb.com.br/",["https://pm-"], [],""], 
               "Cristina": ["https://pm-cristina.publicacao.siplanweb.com.br/",["https://pm-"], [],""], 
               "Guarani": ["https://pm-guarani.publicacao.siplanweb.com.br/",["https://pm-"], [],""], 
               "Coimbra": ["https://pm-coimbra.publicacao.siplanweb.com.br/",["https://pm-"], [],""], 
               #Betha
               "Rio Doce": ["https://e-gov.betha.com.br/transparencia/01037-136/recursos.faces?mun=QEEEuPpMRS0=", ["https://e-gov.be"],[],"?mun=QEEEuPpMRS0="],
               "Alterosa": ["https://transparencia.betha.cloud/#/uA12YSnItzDDIAE8NxlsTA==", ["https://tra"],[]],
               "Itatiaiuçu": ["https://e-gov.betha.com.br/transparencia/01037-136/recursos.faces?mun=l_xE2SVOBCE=", ["https://e-gov.be"],[],"?mun=l_xE2SVOBCE="],
               "Itapeva": ["https://e-gov.betha.com.br/transparencia/01037-136/recursos.faces?mun=l_xE2SVOBCE=", ["https://e-gov.be"],[],"?mun=l_xE2SVOBCE="],
               "Formiga": ["https://e-gov.betha.com.br/transparencia/01037-136/recursos.faces?mun=IOP41QJty3XGuARkGMa-QUl3uQBEf__9", ["https://e-gov.be"],[],"?mun=IOP41QJty3XGuARkGMa-QUl3uQBEf__9"],
               #Sintese e Tecnologia
               "Bonito de Minas": ["http://cidadesmg.com.br/portaltransparencia/faces/user/portal.xhtml?Param=BonitoDeMinas", ["http://ci"],[],""],
               "Gameleiras": ["http://cidadesmg.com.br/portaltransparencia/faces/user/portal.xhtml?Param=Gameleiras", ["http://ci"],[],""],
               "Frei Lagonegro": ["http://cidadesmg.com.br/portaltransparencia/faces/user/portal.xhtml?Param=PMFreiLagoNegro", ["http://ci"],[],""],
               "Catuti": ["http://cidadesmg.com.br/portaltransparencia/faces/user/portal.xhtml?Param=Catuti", ["http://ci"],[],""],
               "Gouveia": ["http://cidadesmg.com.br/portaltransparencia/faces/user/portal.xhtml?Param=Gouveia", ["http://ci"],[],""],
               #ABO
               "Vespasiano": ["http://esic.vespasiano.mg.gov.br/Home/Index/", ["http://esic"],["Download", "VisualizarArquivo", "Detalhes", "Index"],""],
               "Serranos": ["http://transparencia.serranos.mg.gov.br/", ["http://tra"],["Download", "VisualizarArquivo", "Detalhes", "Index"],""],
               "Cristais": ["http://transparencia.cristais.mg.gov.br/", ["http://tra"],["Download", "VisualizarArquivo", "Detalhes", "Index"],""],
               "Brumadinho": ["http://transparencia.brumadinho.mg.gov.br/", ["http://tra"],["Download", "VisualizarArquivo", "Detalhes", "Index"],""],
               "Itabirito": ["http://transparencia.itabirito.mg.gov.br/", ["http://tra"],["Download", "VisualizarArquivo", "Detalhes", "Index"],""],
               #Portal PT
               "Tiradentes": ["https://ptn.tiradentes.mg.gov.br/",["https://ptn"],[],""],
               "Ritápolis": ["http://pt.ritapolis.mg.gov.br", ["https://pt"],[],""],
               "Ingaí": ["http://pt.ingai.mg.gov.br", ["https://pt"],[],""],
               "Prados": ["http://pt.prados.mg.gov.br", ["https://pt"],[],""],
               "Ibituruna": ["http://pt.ibituruna.mg.gov.br", ["https://pt"],[],""],
               #Adpmnet
               "Nova União": ["http://www.adpmnet.com.br/index.php?option=com_contpubl&idorg=26&tpform=1", ["http://www.adpmnet"],[],""],
               "Serro": ["http://www.adpmnet.com.br/index.php?option=com_contpubl&idorg=139&tpform=1", ["http://www.adpmnet"],[],""],
               "Piranguinho": ["http://www.adpmnet.com.br/index.php?option=com_contpubl&idorg=32&tpform=1", ["http://www.adpmnet"],[],""],
               "Paineiras": ["http://adpmnet.com.br/index.php?option=com_contpubl&idorg=454&tpform=1", ["http://www.adpmnet"],[],""],
               "Arinos": ["adpmnet.com.br/index.php?option=com_contpubl&idorg=236&tpform=1", ["http://www.adpmnet"],[],""],    
               #Municipal Net
               "Elói Mendes" : ["https://www.municipalnet.com.br/index/?uid=eloi-mendes", ["https://www.muni"], [],""],
               "Congonhal" : ["https://www.municipalnet.com.br/index/?uid=congonhal", ["https://www.muni"], [],""],
               "Areado" : ["https://www.municipalnet.com.br/index/?uid=areado", ["https://www.muni"], [],""],
               "Coqueiral" : ["https://www.municipalnet.com.br/index/?uid=coqueiral", ["https://www.muni"], [],""],
               "Albertina" : ["https://www.municipalnet.com.br/index/?uid=albertina", ["https://www.muni"], [],""],
               #Portal Facil (60)
               "Antônio Dias": ["https://www.antoniodias.mg.gov.br/transparencia", ["https://www.an"], [],""], 
               "Itaobim": ["https://www.itaobim.mg.gov.br/transparencia", ["https://www.it"], [],""], 
               "Três Marias": ["https://www.tresmarias.mg.gov.br/transparencia", ["https://www.tr"], [],""],
               "Paraopeba": ["https://www.paraopeba.mg.gov.br/transparencia", ["https://www.par"], [],""],
               "Raul Soares": ["https://www.raulsoares.mg.gov.br/transparencia", ["https://www.raul"], [],""],
               #Portal Facil (46)
               "Caputira": ["http://www.transparenciafacil.com.br/0147902", ["https://tr"], [],""], 
               "Guaraciaba": ["http://www.transparenciafacil.com.br/0165702", ["https://tr"], [],""],
               "Santo Antônio do Grama": ["http://www.transparenciafacil.com.br/0203702", ["https://tr"], [],""],
               "Claraval": ["http://www.transparenciafacil.com.br/0151802", ["https://tr"], [],""],
               "Heliodora": ["http://www.transparenciafacil.com.br/0166802", ["https://tr"], [],""],
                #Memory
               "Perdigão": ["http://lai.memory.com.br/entidades/login/9CC4C5", ["https://la"], [],""],
               "Martinho Campos": ["http://lai.memory.com.br/entidades/login/9BG219", ["https://la"], [],""],
               "Matozinhos": ["http://lai.memory.com.br/entidades/login/9BHSQH", ["https://la"], [],""],
               "Salinas": ["http://lai.memory.com.br/entidades/login/9D2D8L", ["https://la"], [],""],
               "Pitangui": ["http://lai.memory.com.br/entidades/login/9CHA9H", ["https://la"], [],""],
               #GRP
               "Conquista" : ["http://portal.conquista.mg.gov.br:8080/portalcidadao/", ["http://po"], [],""],
               "Divinópolis" : ["https://cidadao.divinopolis.mg.gov.br/portalcidadao/", ["https://cid"], [],""],
               "Caxambu" : ["http://170.254.192.42:8080/portalcidadao/", ["http://170"], [],""],
               "Guaxupé" : ["https://ts.guaxupe.mg.gov.br/portalcidadao/", ["https://ts.gua"], [],""],
               "Andradas" : ["https://sonner.andradas.mg.gov.br/portalcidadao/", ["https://son"], [],""],
               #Template 1 (22)
               "Conceição das Alagoas" : ["http://187.72.75.161:8444/transparencia/", ["http://187"], [],""],
               "Pratinha" : ["http://201.71.44.3:8445/transparencia/", ["http://201"], [],""],
               "Estrela do Sul" : ["http://187.44.64.138:8445/transparencia/", ["http://187"], [],""],
               "Cruzeiro da Fortaleza" : ["http://138.0.67.146:8444/transparencia/", ["http://138"], [],""],
               "Rio Paranaíba" : ["http://prefriopara.ddns.net:8444/transparencia/", ["http://pre"], [],""],
               #Template 1 (9)
               "Belo Horizonte" : ["https://transparencia.pbh.gov.br/bh_prd_transparencia/web/", ["https://tran", "https://pre"], [],""],
               "Itamonte" : ["http://transparencia.itamonte.mg.gov.br/", ["https://tran"], [],""],
               "Cidade1" : ["", [], [],""],
               "Cidade2" : ["", [], [],""],
               "Cidade3" : ["", [], [],""]}


cidades = cidades_dic.keys()

df = pd.DataFrame(False, index = cidades, columns = tags)

df_templates = pd.DataFrame(index = cidades, columns = ["Template"])


df_templates.loc['Frei Gaspar']["Template"] = "Template 2" 
df_templates.loc['Coroaci']["Template"] = "Template 2"  
df_templates.loc['Machacalis']["Template"] = "Template 2" 
df_templates.loc['Sardoá']["Template"] = "Template 2"  
df_templates.loc['Cuparaque']["Template"] = "Template 2"  

df_templates.loc['Abre Campo']["Template"] = "Portal TP" 
df_templates.loc['Manhuaçu']["Template"] = "Portal TP"
df_templates.loc['Almenara']["Template"] = "Portal TP" 
df_templates.loc['São Geraldo do Baixio']["Template"] = "Portal TP"
df_templates.loc['João Monlevade']["Template"] = "Portal TP" 

df_templates.loc['Rio Doce']["Template"] = "Betha"
df_templates.loc['Alterosa']["Template"] = "Betha"
df_templates.loc['Itatiaiuçu']["Template"] = "Betha"
df_templates.loc['Itapeva']["Template"] = "Betha"
df_templates.loc['Formiga']["Template"] = "Betha"

df_templates.loc['Aracitaba']["Template"] = "Siplanweb"
df_templates.loc['Cruzília']["Template"] = "Siplanweb"
df_templates.loc['Cristina']["Template"] = "Siplanweb"
df_templates.loc['Guarani']["Template"] = "Siplanweb"
df_templates.loc['Coimbra']["Template"] = "Siplanweb"

df_templates.loc['Bonito de Minas']["Template"] = "Sintese e Tecnologia"  
df_templates.loc['Gameleiras']["Template"] = "Sintese e Tecnologia" 
df_templates.loc['Frei Lagonegro']["Template"] = "Sintese e Tecnologia" 
df_templates.loc['Catuti']["Template"] = "Sintese e Tecnologia" 
df_templates.loc['Gouveia']["Template"] = "Sintese e Tecnologia" 

df_templates.loc['Vespasiano']["Template"] = "ABO"
df_templates.loc['Serranos']["Template"] = "ABO"
df_templates.loc['Cristais']["Template"] = "ABO"
df_templates.loc['Brumadinho']["Template"] = "ABO"
df_templates.loc['Itabirito']["Template"] = "ABO"

df_templates.loc['Tiradentes']["Template"] = "PT"
df_templates.loc['Ritápolis']["Template"] = "PT"
df_templates.loc['Ingaí']["Template"] = "PT"
df_templates.loc['Prados']["Template"] = "PT"
df_templates.loc['Ibituruna']["Template"] = "PT"

df_templates.loc['Nova União']["Template"] = "ADPM"
df_templates.loc['Serro']["Template"] = "ADPM"
df_templates.loc['Piranguinho']["Template"] = "ADPM"
df_templates.loc['Paineiras']["Template"] = "ADPM"
df_templates.loc['Arinos']["Template"] = "ADPM"
                   
df_templates.loc['Elói Mendes']["Template"] = "Municipal Net"
df_templates.loc['Congonhal']["Template"] = "Municipal Net"
df_templates.loc['Areado']["Template"] = "Municipal Net"
df_templates.loc['Coqueiral']["Template"] = "Municipal Net"
df_templates.loc['Albertina']["Template"] = "Municipal Net"

df_templates.loc['Conquista']["Template"] = "GRP"
df_templates.loc['Divinópolis']["Template"] = "GRP"
df_templates.loc['Caxambu']["Template"] = "GRP"
df_templates.loc['Guaxupé']["Template"] = "GRP"
df_templates.loc['Andradas']["Template"] = "GRP"

df_templates.loc['Belo Horizonte']["Template"] = "Template 1 (9)"
df_templates.loc['Itamonte']["Template"] = "Template 1 (9)"
df_templates.loc['Cidade1']["Template"] = "Template 1 (9)"
df_templates.loc['Cidade2']["Template"] = "Template 1 (9)"
df_templates.loc['Cidade3']["Template"] = "Template 1 (9)"

df_templates.loc['Conceição das Alagoas']["Template"] = "Template 1 (22)"
df_templates.loc['Rio Paranaíba']["Template"] = "Template 1 (22)"
df_templates.loc['Cruzeiro da Fortaleza']["Template"] = "Template 1 (22)"
df_templates.loc['Pratinha']["Template"] = "Template 1 (22)"
df_templates.loc['Estrela do Sul']["Template"] = "Template 1 (22)"
    
df_templates.loc['Antônio Dias']["Template"] = "Portal Facil (60)" 
df_templates.loc['Itaobim']["Template"] = "Portal Facil (60)"
df_templates.loc['Três Marias']["Template"] = "Portal Facil (60)" 
df_templates.loc['Paraopeba']["Template"] = "Portal Facil (60)"
df_templates.loc['Raul Soares']["Template"] = "Portal Facil (60)" 

df_templates.loc['Caputira']["Template"] = "Portal Facil (46)" 
df_templates.loc['Guaraciaba']["Template"] = "Portal Facil (46)" 
df_templates.loc['Claraval']["Template"] = "Portal Facil (46)" 
df_templates.loc['Heliodora']["Template"] = "Portal Facil (46)" 
df_templates.loc['Santo Antônio do Grama']["Template"] = "Portal Facil (46)" 
    
df_templates.loc['Perdigão']["Template"] = "Memory" 
df_templates.loc['Martinho Campos']["Template"] = "Memory" 
df_templates.loc['Matozinhos']["Template"] = "Memory" 
df_templates.loc['Salinas']["Template"] = "Memory" 
df_templates.loc['Pitangui']["Template"] = "Memory" 


# In[54]:


df


# In[56]:


df_templates


# In[55]:


for key, value in cidades_dic.items():
    crawl([value[0]], 3, kwtree, df, key, [value[1], value[2]], value[3])


# In[148]:


df_completo = df_templates.join(df)
df_completo


# In[149]:


def merge_found_values(x):

    results = []
    l = [False]*(x.shape[0])

    i = 0
    for line in x:
        for element in line:
            l[i] = element or l[i]
        i+=1 

    for n in range(0,len(l),5):
        results.append(l[n] or l[n+1] or l[n+2] or l[n+3] or l[n+4])

    return np.array(results).T
  


# In[150]:


templates = ['Template 2',
       'Portal TP',
       'Siplanweb',
       'Betha',
       'Sintese e Tecnologia',
       'ABO',
       'PT',
       'ADPM',
       'Municipal Net',
       'Portal Facil (60)',
       'Portal Facil (46)',
       'Memory',
       'GRP',
       'Template 1 (22)',
       'Template 1 (9)']

subtags = ["Informações", "Licitações", "Empenhos", "Pagamentos", "Relatorios", 'Leis Orçamentárias', "Contas Públicas", "Contratos", "Concurso Publico", "Receitas","Terceiro Setor", "Orçamento", "Obras", "Servidores" , "Diárias", "Estrutura Organizacional", "Plano de Metas"]
df_resultados = pd.DataFrame(index = templates)

df_resultados["Informações"] = 	merge_found_values(df_completo[["Transparência", "12.527/2011", "45.969/2012",	"www.transparencia.mg.gov.br",	"Lei de Acesso à Informação",	"CODEMA",	"CMDCA",	"F.A.Q", "FAQ",	"Perguntas Frequentes",	"Pedidos",	"Estrutura Organizacional",	"Endereço",	"Telefone",	"Horário de Atendimento",	"Conselhos Municipais"]].to_numpy())	
df_resultados["Licitações"] = merge_found_values(df_completo[["Licitaç"]].to_numpy())	
df_resultados["Repasses"] = merge_found_values(df_completo[["Repasse"]].to_numpy())	
df_resultados["Empenhos"] = merge_found_values(df_completo[["Empenhos",	"N° de empenho",	"N° do empenho"]].to_numpy())
df_resultados["Pagamentos"] = merge_found_values(df_completo[["Pagamentos", "Pagar"]].to_numpy())
df_resultados["Relatorios"] = merge_found_values(df_completo[["Gestão fiscal", 	"Resumido de Execução" ]].to_numpy())
df_resultados["Leis Orçamentárias"] = merge_found_values(df_completo[["Plano Plurianual",  "Diretrizes",	"Orçament"]].to_numpy())
df_resultados["Contas Públicas"] = merge_found_values(df_completo[[ "Balanço", "Contas", "Prestação"	]].to_numpy())
df_resultados["Contratos"] = merge_found_values(df_completo[["Contrato","Vigência"]].to_numpy())
df_resultados["Concurso Publico"] = merge_found_values(df_completo[["Concurso", "Concurso Público"]].to_numpy())
df_resultados["Receitas"] = merge_found_values(df_completo[["Receitas",	"Consolidado", "Liquida",	"Previs",	"Arrecada"]].to_numpy())
df_resultados["Terceiro Setor"] = merge_found_values(df_completo[["Terceiro Setor",	"Parcerias",	"Repasses", "Convênios"]].to_numpy())
df_resultados["Orçamento"] = merge_found_values(df_completo[["Orçament"]].to_numpy())
df_resultados["Conselhos Municipais"] = merge_found_values(df_completo[["Conselho", "CODEMA", "CMDCA"]].to_numpy())
df_resultados["Servidores"] = merge_found_values(df_completo[["Servidor", "Relatorio Mensal",	"Despesa com Pessoal",	"Despesas com pessoal"]].to_numpy())
df_resultados["Diárias"] = merge_found_values(df_completo[["Diária", "Viagen",	"Viagem",	"Destino"]].to_numpy())
df_resultados["Obras"] = merge_found_values(df_completo[["Obra"]].to_numpy())
df_resultados["Estrutura Organizacional"] = merge_found_values(df_completo[["Estrutura Organizacional"]].to_numpy())
df_resultados["Plano de Metas"] = merge_found_values(df_completo[["Meta", "Plano de Metas"]].to_numpy())
df_resultados["Legislação"] = merge_found_values(df_completo[["Legisl"]].to_numpy())


# In[152]:


df_resultados


# In[153]:


df_resultados.to_csv("resultados_templates.csv")


# ## Busca cidades

# In[6]:


cidades_isoladas = {"Uberlândia (prefeitura)": ["https://www.uberlandia.mg.gov.br/",["https://www.uber"], ["transparencia"],""],
                    "Uberlândia (transparencia)": ["https://www.uberlandia.mg.gov.br/portal-da-transparencia/",["https://www.uberlandia.mg.gov.br/portal"], [],""],
                    "Juiz de Fora (prefeitura)": ["https://www.pjf.mg.gov.br/",["https://www.pjf"], ["transparencia"],""],
                    "Juiz de Fora (transparencia)": ["https://www.pjf.mg.gov.br/transparencia/",["https://www.pjf.mg.gov.br/transparencia"], [],""],
                    "Betim (prefeitura)": ["https://www.betim.mg.gov.br/",["https://www.bet"], [],""],
                    "Betim (transparencia)": ["http://servicos.betim.mg.gov.br/appsgi/servlet/wmtranspinicial",[], [],""],
                    "Teófilo Otoni (prefeitura)": ["https://teofilootoni.mg.gov.br/",["https://teofi"], [],""],
                    "Teófilo Otoni (transparencia)": ["https://transparencia.teofilootoni.mg.gov.br/portalcidadao/",[], [],""],
                    "Varginha (prefeitura)": ["https://www.varginha.mg.gov.br/",["https://www.vargi"], [],""],
                    "Varginha (transparencia)": ["https://leideacesso.etransparencia.com.br/varginha.prefeitura.mg/TDAPortalClient.aspx?417",["https://leideacesso"], [],""]}


# In[7]:


cidades = cidades_isoladas.keys()
df_cidades = pd.DataFrame(False, index = cidades, columns = tags)
df_cidades


# In[ ]:


for key, value in cidades_isoladas.items():
    crawl([value[0]], 3, kwtree, df_cidades, key, [value[1], value[2]], value[3])


# In[48]:


def merge_found_values_cities(x):

    results = [False]*(x.shape[0])

    i = 0
    for line in x:
        print(line)
        for element in line:
            results[i] = element or results[i]
        i+=1 

    return np.array(results).T


# In[49]:


subtags = ["Informações", "Licitações", "Empenhos", "Pagamentos", "Relatorios", 'Leis Orçamentárias', "Contas Públicas", "Contratos", "Concurso Publico", "Receitas","Terceiro Setor", "Orçamento", "Obras", "Servidores" , "Diárias", "Estrutura Organizacional", "Plano de Metas"]
df_resultados_cidades = pd.DataFrame(index = cidades)

df_resultados_cidades["Informações"] = 	merge_found_values_cities(df_cidades[["Transparência", "12.527/2011", "45.969/2012",	"www.transparencia.mg.gov.br",	"Lei de Acesso à Informação",	"CODEMA",	"CMDCA",	"F.A.Q", "FAQ",	"Perguntas Frequentes",	"Pedidos",	"Estrutura Organizacional",	"Endereço",	"Telefone",	"Horário de Atendimento",	"Conselhos Municipais"]].to_numpy())	
df_resultados_cidades["Licitações"] = merge_found_values_cities(df_cidades[["Licitaç"]].to_numpy())	
df_resultados_cidades["Repasses"] = merge_found_values_cities(df_cidades[["Repasse"]].to_numpy())	
df_resultados_cidades["Empenhos"] = merge_found_values_cities(df_cidades[["Empenhos",	"N° de empenho",	"N° do empenho"]].to_numpy())
df_resultados_cidades["Pagamentos"] = merge_found_values_cities(df_cidades[["Pagamentos", "Pagar"]].to_numpy())
df_resultados_cidades["Relatorios"] = merge_found_values_cities(df_cidades[["Gestão fiscal", 	"Resumido de Execução" ]].to_numpy())
df_resultados_cidades["Leis Orçamentárias"] = merge_found_values_cities(df_cidades[["Plano Plurianual",  "Diretrizes",	"Orçament"]].to_numpy())
df_resultados_cidades["Contas Públicas"] = merge_found_values_cities(df_cidades[[ "Balanço", "Contas", "Prestação"	]].to_numpy())
df_resultados_cidades["Contratos"] = merge_found_values_cities(df_cidades[["Contrato","Vigência"]].to_numpy())
df_resultados_cidades["Concurso Publico"] = merge_found_values_cities(df_cidades[["Concurso", "Concurso Público"]].to_numpy())
df_resultados_cidades["Receitas"] = merge_found_values_cities(df_cidades[["Receitas",	"Consolidado", "Liquida",	"Previs",	"Arrecada"]].to_numpy())
df_resultados_cidades["Terceiro Setor"] = merge_found_values_cities(df_cidades[["Terceiro Setor",	"Parcerias",	"Repasses", "Convênios"]].to_numpy())
df_resultados_cidades["Orçamento"] = merge_found_values_cities(df_cidades[["Orçament"]].to_numpy())
df_resultados_cidades["Conselhos Municipais"] = merge_found_values_cities(df_cidades[["Conselho", "CODEMA", "CMDCA"]].to_numpy())
df_resultados_cidades["Servidores"] = merge_found_values_cities(df_cidades[["Servidor", "Relatorio Mensal",	"Despesa com Pessoal",	"Despesas com pessoal"]].to_numpy())
df_resultados_cidades["Diárias"] = merge_found_values_cities(df_cidades[["Diária", "Viagen",	"Viagem",	"Destino"]].to_numpy())
df_resultados_cidades["Obras"] = merge_found_values_cities(df_cidades[["Obra"]].to_numpy())
df_resultados_cidades["Estrutura Organizacional"] = merge_found_values_cities(df_cidades[["Estrutura Organizacional"]].to_numpy())
df_resultados_cidades["Plano de Metas"] = merge_found_values_cities(df_cidades[["Meta", "Plano de Metas"]].to_numpy())
df_resultados_cidades["Legislação"] = merge_found_values_cities(df_cidades[["Legisl"]].to_numpy())


# In[50]:


df_resultados_cidades.to_csv("resultados_cidades.csv")


# In[51]:


df_resultados_cidades


# In[ ]:




