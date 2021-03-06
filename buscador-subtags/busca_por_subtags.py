# -*- coding: utf-8 -*-

#!pip install ahocorapy

import urllib3
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ahocorapy.keywordtree import KeywordTree

def getText(html):

  for tags in html(['script', 'style']):
    tags.decompose

  return ' '. join(html.stripped_strings)

def findPatterns(text, tree, page, df, cidade):

  results = kwtree.search_all(text)
  results = [result[0] for result in results]
  results_unique = set(results)

  for result in results_unique:
    #if results.count(result) > 1: #para exigir que resultados so sejam validos se ocorrerem mais de uma vez na pagina
    print("\"" + result + "\" found " + str(results.count(result)) + " time(s) on page: " + page)
    df.loc[cidade][result] = True
    
  if len(results) != 0:
    print("\n")

  return df

def crawl(pages, depth, kwtree, df, cidade, restrictions):
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  already_visited = set(pages)

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
      text = getText(soup)
      df = findPatterns(text, kwtree, page, df, cidade)
      already_visited.add(page)

      links = soup.find_all('a')
      counter = 0

      for link in links:
        url = ""

        if("href" in link.attrs):
          url = urljoin(page, str(link.get('href')))

          if url.find("'") != -1:
            continue

          url = url.split("#")[0]

        
        is_valid = False

        #Restriction to prevent the crawler get out the base url
        for rest in restrictions[0]:
          if url.startswith(rest):
            is_valid = True
    
        for rest in restrictions[1]:
          if rest in url:
            is_valid = False
            break
        
        if is_valid:
          new_pages.add(url)

        counter += 1
    
    pages = new_pages.difference(already_visited)

  print("Number of links visited: " +  str(len(already_visited)))

  return df

kwtree = KeywordTree(case_insensitive=True)

#tags = ["Plano Plurianual", "Aux??lios", "Aposentadoria", "Pens??o", "Parceria", "Repasse", "Conselho", "Lei de Diretrizes", "Fiscal", "Viagens", "Resumido", "Modalidade", "Folha Pagamento", "Liquidado", "Planejamento", "Fatura", "Consolidado", "Previsto", "Arrecadado", "Concurso", "Vigencia", "Preg??o Presencial", "Relat??rios", "Servidores", "Obra", "Meta"]
#tags = ["Concurso","Plano", "Metas", "Terceiro setor", "Repasse", "Servidor", "Parceria"]
#tags = ["12.527/2011", "45.969/2012", "www.transparencia.mg.gov.br", " Lei de Acesso ?? Informa????o", "CODEMA", "CMDCA"]
tags = ["Transpar??ncia", "12.527/2011", "45.969/2012", "www.transparencia.mg.gov.br", "Lei de Acesso ?? Informa????o", "CODEMA", "CMDCA", "F.A.Q", "FAQ", "Perguntas Frequentes", "Pedidos", "Estrutura Organizacional", "Endere??o", "Telefone", "Hor??rio de Atendimento", "Conselhos Municipais", "Receitas", "Consolidado", "Liquida", "Previs", "Arrecada", "Classifica????o","Balan??o", "Contas", "Meta", "Plano de Metas", "Gest??o fiscal", "Resumido de Execu????o", "Diretrizes", "Or??ament",  "Pagamentos", "Pagar", "Empenhos", "N?? de empenho", "N?? do empenho", "Valor", "Favorecido", "Licita??", "Status", "Modalidade", "Resultado", "Status","Contrato", "Vig??ncia", "Terceiro Setor", "Parcerias", "Repasses", "Data de celebra????o", "Data", "Conveniado", "Origem", "Recurso", "Concurso", "Conselho", "Pens??o", "Plano Plurianual", "Concurso P??blico", "Obra", "Situa????o", "Servidor", "Nome", "Cargo", "Fun????o", "Relatorio Mensal", "Despesa com Pessoal", "Despesas com pessoal", "Aposentado", "Pensionista", "Di??ria", "Viagen", "Viagem", "Periodo", "Conv??nios", "Destino", "Motivo", "Presta????o"]

for tag in tags:
  kwtree.add(tag)
kwtree.finalize()

pd.set_option('max_columns', None)

cidades_dic = {"Frei Gaspar": ["https://freigaspar.mg.gov.br/transparencia",["https://fr"], ["detalhes", "noticias"]],
               "Coroaci": ["https://coroaci.mg.gov.br/transparencia",["https://co"], ["detalhes", "noticias"]], 
               "Ant??nio Dias": ["https://www.antoniodias.mg.gov.br/transparencia", ["https://an"], []], 
               "Itaobim": ["https://www.itaobim.mg.gov.br/transparencia", ["https://it"], []], 
               "Caputira": ["http://www.transparenciafacil.com.br/0147902", ["https://tr"], []], 
               "Guaraciaba": ["http://www.transparenciafacil.com.br/0165702", ["https://tr"], []], 
               "Abre Campo": ["https://abrecampo-mg.portaltp.com.br/", ["https://ab"], ["consultas"]],
               "Manhua??u": ["https://manhuacu-mg.portaltp.com.br/", ["https://ma"], ["consultas"]],
               "Perdig??o": ["http://lai.memory.com.br/entidades/login/9CC4C5", ["https://la"], []],
               "Martinho Campos": ["http://lai.memory.com.br/entidades/login/9BG219", ["https://la"], []],
               "Aracitaba": ["https://pm-aracitaba.publicacao.siplanweb.com.br/",["https://pm-"], []], 
               "Cruz??lia": ["https://pm-cruzilia.publicacao.siplanweb.com.br/",["https://pm-"], []], 
               "Rio Doce": ["https://e-gov.betha.com.br/transparencia/01037-136/recursos.faces?mun=QEEEuPpMRS0=", ["https://e-gov.be"],[]],
               "Alterosa": ["https://transparencia.betha.cloud/#/uA12YSnItzDDIAE8NxlsTA==", ["https://tra"],[]],
               "Bonito de Minas": ["http://cidadesmg.com.br/portaltransparencia/faces/user/portal.xhtml?Param=BonitoDeMinas", ["http://ci"],[]],
               "Gameleiras": ["http://cidadesmg.com.br/portaltransparencia/faces/user/portal.xhtml?Param=Gameleiras", ["http://ci"],[]],
               "Vespasiano": ["http://esic.vespasiano.mg.gov.br/Home/Index/", ["http://esic"],["Download", "VisualizarArquivo", "Detalhes", "Index"]],
               "Serranos": ["http://transparencia.serranos.mg.gov.br/", ["http://tra"],["Download", "VisualizarArquivo", "Detalhes", "Index"]],
               "Tiradentes": ["https://ptn.tiradentes.mg.gov.br/",["https://ptn"],[]],
               "Rit??polis": ["https://pt.ritapolis.mg.gov.br", ["https://pt"],[]],
               "Nova Uni??o": ["http://www.adpmnet.com.br/index.php?option=com_contpubl&idorg=26&tpform=1", ["http://www.adpmnet"],[]],
               "Serro": ["http://www.adpmnet.com.br/index.php?option=com_contpubl&idorg=139&tpform=1", ["http://www.adpmnet"],[]],
               "El??i Mendes" : ["https://www.municipalnet.com.br/index/?uid=eloi-mendes", ["https://www.muni"], []],
               "Congonhal" : ["https://www.municipalnet.com.br/index/?uid=congonhal", ["https://www.muni"], []],
               "Conquista" : ["http://portal.conquista.mg.gov.br:8080/portalcidadao/", ["http://po"], []],
               "Divin??polis" : ["https://cidadao.divinopolis.mg.gov.br/portalcidadao/", ["https://cid"], []],
               "Belo Horizonte" : ["https://transparencia.pbh.gov.br/bh_prd_transparencia/web/", ["https://tran", "https://pre"], []],
               "Itamonte" : ["http://transparencia.itamonte.mg.gov.br/", ["https://tran"], []],
               "Concei????o das Alagoas" : ["http://187.72.75.161:8444/transparencia/", ["http://187"], []],
               "Rio Parana??ba" : ["http://prefriopara.ddns.net:8444/transparencia/", ["http://pre"], []]}

cidades = cidades_dic.keys()

df = pd.DataFrame(False, index = cidades, columns = tags)

df_templates = pd.DataFrame(index = cidades, columns = ["Template"]);

df_templates.loc['Frei Gaspar']["Template"] = "Template 2" 
df_templates.loc['Coroaci']["Template"] = "Template 2"  
df_templates.loc['Ant??nio Dias']["Template"] = "Portal F??cil (60)" 
df_templates.loc['Itaobim']["Template"] = "Portal F??cil (60)" 
df_templates.loc['Caputira']["Template"] = "Portal F??cil (46)" 
df_templates.loc['Guaraciaba']["Template"] = "Portal F??cil (46)" 
df_templates.loc['Abre Campo']["Template"] = "Portal TP" 
df_templates.loc['Manhua??u']["Template"] = "Portal TP" 
df_templates.loc['Perdig??o']["Template"] = "Memory" 
df_templates.loc['Martinho Campos']["Template"] = "Memory" 
df_templates.loc['Rio Doce']["Template"] = "Betha"
df_templates.loc['Alterosa']["Template"] = "Betha"
df_templates.loc['Aracitaba']["Template"] = "Siplanweb"
df_templates.loc['Cruz??lia']["Template"] = "Siplanweb"
df_templates.loc['Bonito de Minas']["Template"] = "Sintese e Tecnologia"  
df_templates.loc['Gameleiras']["Template"] = "Sintese e Tecnologia"  
df_templates.loc['Vespasiano']["Template"] = "ABO"
df_templates.loc['Serranos']["Template"] = "ABO"
df_templates.loc['Tiradentes']["Template"] = "PT"
df_templates.loc['Rit??polis']["Template"] = "PT"
df_templates.loc['Nova Uni??o']["Template"] = "ADPM"
df_templates.loc['Serro']["Template"] = "ADPM"
df_templates.loc['El??i Mendes']["Template"] = "Municipal Net"
df_templates.loc['Congonhal']["Template"] = "Municipal Net"
df_templates.loc['Conquista']["Template"] = "GRP"
df_templates.loc['Divin??polis']["Template"] = "GRP"
df_templates.loc['Belo Horizonte']["Template"] = "Template 1 (9)"
df_templates.loc['Itamonte']["Template"] = "Template 1 (9)"
df_templates.loc['Concei????o das Alagoas']["Template"] = "Template 1 (22)"
df_templates.loc['Rio Parana??ba']["Template"] = "Template 1 (22)"

df

df_templates

for key, value in cidades_dic.items():
  df = crawl([value[0]], 3, kwtree, df, key, [value[1], value[2]])

df_completo = df_templates.join(df)
df_completo

def merge_found_values(x):

  results = []
  l = [False]*(x.shape[0])

  i = 0
  for line in x:
    for element in line:
      l[i] = element or l[i]
    i+=1 

  for n in range(0,len(l),2):
    results.append(l[n] or l[n+1])

  return np.array(results).T

templates = ['Template 2',
       'Porta F??cil (60)',
       'Porta F??cil (46)',
       'Portla TP',
       'Memory',
       'Siplanweb',
       'Betha',
       'Sintese e Tecnologia',
       'ABO',
       'PT',
       'ADPM',
       'Municipal Net',
       'GRP',
       'Template 1 (9)',
       'Template 1 (22)']

subtags = ["Informa????es", "Licita????es", "Empenhos", "Pagamentos", "Relatorios", 'Leis Or??ament??rias', "Contas P??blicas", "Contratos", "Concurso Publico", "Receitas","Terceiro Setor", "Or??amento", "Obras", "Servidores" , "Di??rias", "Estrutura Organizacional", "Plano de Metas"]
df_resultados = pd.DataFrame(index = templates)

df_resultados["Informa????es"] = 	merge_found_values(df_completo[["Transpar??ncia", "12.527/2011", "45.969/2012",	"www.transparencia.mg.gov.br",	"Lei de Acesso ?? Informa????o",	"CODEMA",	"CMDCA",	"F.A.Q", "FAQ",	"Perguntas Frequentes",	"Pedidos",	"Estrutura Organizacional",	"Endere??o",	"Telefone",	"Hor??rio de Atendimento",	"Conselhos Municipais"]].to_numpy())	
df_resultados["Licita????es"] = merge_found_values(df_completo[["Licita??"]].to_numpy())	
df_resultados["Empenhos"] = merge_found_values(df_completo[["Empenhos",	"N?? de empenho",	"N?? do empenho"]].to_numpy())
df_resultados["Pagamentos"] = merge_found_values(df_completo[["Pagamentos", "Pagar"]].to_numpy())
df_resultados["Relatorios"] = merge_found_values(df_completo[["Gest??o fiscal", 	"Resumido de Execu????o" ]].to_numpy())
df_resultados["Leis Or??ament??rias"] = merge_found_values(df_completo[["Plano Plurianual",  "Diretrizes",	"Or??ament"]].to_numpy())
df_resultados["Contas P??blicas"] = merge_found_values(df_completo[[ "Balan??o", "Contas", "Presta????o"	]].to_numpy())
df_resultados["Contratos"] = merge_found_values(df_completo[["Contrato","Vig??ncia"]].to_numpy())
df_resultados["Concurso Publico"] = merge_found_values(df_completo[["Concurso", "Concurso P??blico"]].to_numpy())
df_resultados["Receitas"] = merge_found_values(df_completo[["Receitas",	"Consolidado", "Liquida",	"Previs",	"Arrecada"]].to_numpy())
df_resultados["Terceiro Setor"] = merge_found_values(df_completo[["Terceiro Setor",	"Parcerias",	"Repasses", "Conv??nios"]].to_numpy())
df_resultados["Or??amento"] = merge_found_values(df_completo[["Or??ament"]].to_numpy())
df_resultados["Servidores"] = merge_found_values(df_completo[["Servidor", "Relatorio Mensal",	"Despesa com Pessoal",	"Despesas com pessoal"]].to_numpy())
df_resultados["Di??rias"] = merge_found_values(df_completo[["Di??ria", "Viagen",	"Viagem",	"Destino"]].to_numpy())
df_resultados["Obras"] = merge_found_values(df_completo[["Obra"]].to_numpy())
df_resultados["Estrutura Organizacional"] = merge_found_values(df_completo[["Estrutura Organizacional"]].to_numpy())
df_resultados["Plano de Metas"] = merge_found_values(df_completo[["Meta", "Plano de Metas"]].to_numpy())

df_resultados

df_resultados.to_csv("resultados_templates.csv")

