from github import Github
from github3 import login
import streamlit as st
import zipfile
from zipfile import ZipFile
from io import BytesIO
import json
import time
from io import StringIO
import os
import glob
import shutil
from unidecode import unidecode
import requests

import random

API_ADDRESS = 'http://10.21.0.130:8000/api/crawlers/'

def source_name_replace(data, tag, subtag, nome_municipio):

    data['source_name'] = data['source_name'].replace("<TAG>", tag)
    data['source_name'] = data['source_name'].replace("<SUBTAG>", subtag)
    data['source_name'] = data['source_name'].replace("<NOME_MUNICIPIO>", nome_municipio)
    
    return data
    
def data_path_replace(data, tag, subtag, municipio_path):

    data['data_path'] = data['data_path'].replace("<TAG>", unidecode(tag).lower())
    data['data_path'] = data['data_path'].replace("<SUBTAG>", unidecode(subtag).lower())
    data['data_path'] = data['data_path'].replace("<MUNICIPIO_PATH>", unidecode(municipio_path).lower().replace(" ", "_"))
    
    return data
    
def base_url_replace(data, url_base, param_url):

    data['base_url'] = data['base_url'].replace("<URL_BASE>", url_base)
    data['base_url'] = data['base_url'].replace("<PARAM_URL>", param_url)
    
    return data
    
def fill_config_file(template, config, tag, subtag, url_base):
    
    configs = []
    for nome_municipio, parametros in config.items():

        data = source_name_replace(template.copy(), tag, subtag, nome_municipio)
       
        for key, value in parametros.items():
            if  key == 'param_url':  
                data = base_url_replace(data, url_base, value)
            elif key == 'data_path':
                data = data_path_replace(data, tag, subtag, value)
        
        configs.append(data)

    return configs

def create_and_run_coletor(config):
    
    #if not os.path.exists(config['data_path']):
    #    os.makedirs(config['data_path'])

    try:
        r_creator = requests.post(API_ADDRESS, data=config)
        configuracao_do_coletor_criado = r_creator.json()
    
        id_crawler = configuracao_do_coletor_criado['id']
        
        print(f'ID do coletor criado: {id_crawler}')
    
        r_run = requests.get(API_ADDRESS + f'{id_crawler}/run')
    
        time.sleep(5)
        
    except KeyError as error:
        st.error('KeyError: json devolvido = ' + str(r_creator.json()))    
        raise error
    return r_creator
    
def app1():
    
    user=""
    configs = ''
    
    st.title("Generalização de configuração de coleta")

    template_name = st.text_input("Entre com o nome do template:")
    
    url_base = st.text_input("Entre com a url base:")
    
    tag = st.text_input("Entre com a tag da solicitação (sem espaços):")
    
    subtag = st.text_input("Entre com a subtag da solicitação (sem espaços):")
      
    template_file = st.file_uploader("Carregue o template de configuração aqui")
    if template_file is not None:
        template = json.load(template_file)
    
    config_file = st.file_uploader("Carregue o arquivo com as informações a serem inseridas na configuração aqui")
    if config_file is not None:
        config = json.load(config_file)
    
    b1 = st.checkbox('Gerar configurações', key=0)
    if b1:
        
        configs = fill_config_file(template, config, tag, subtag, url_base)
        
        if not os.path.exists('{}_{}_{}'.format(template_name, tag, subtag)):
            os.makedirs('{}_{}_{}'.format(template_name, tag, subtag))
        
        i = 0
        for nome_municipio, _ in config.items():
            with open('{}_{}_{}/config_{}.json'.format(template_name, tag, subtag, nome_municipio), 'w') as f:
                json.dump(configs[i], f, indent=4) 
            i+=1
        
        shutil.make_archive('{}_{}_{}'.format(template_name, tag, subtag), 'zip', '{}_{}_{}/'.format(template_name, tag, subtag))
        
        st.markdown("### Atenção humano, você está prestes a criar {} coletores! Muita calma nessa hora.".format(len(configs)))
        
        
        with open('{}_{}_{}.zip'.format(template_name, tag, subtag), "rb") as fp:
            st.download_button(
             label="Download",
             data=fp,
             file_name='config.zip'
             )
        
        shutil.rmtree('{}_{}_{}'.format(template_name, tag, subtag))
        os.remove('{}_{}_{}.zip'.format(template_name, tag, subtag))
     
    
        b2 = st.button('Criar e rodar coletores', key=1)
        if b2:
            
            for i in configs:
                create_and_run_coletor(i)
            
def app2():
    st.title("Criador de Coletores")
    
    zip_file = st.file_uploader("Carregue o zip com as configurações de coleta aqui")
    
    hash = random.getrandbits(128)
    
    if zip_file is not None:
        shutil.unpack_archive(zip_file, 'configs/temp_{}'.format(hash), 'zip')
        
        files = glob.glob(f"configs/temp_{hash}/*.json")
        
        st.markdown("### Atenção humano, você está prestes a criar {} coletores! Muita calma nessa hora.".format(len(files)))
        
        b1 = st.button('Criar e rodar coletores', key=3)
        if b1:         
                 
            for file in files:
                with open(file, 'r') as f:
                    config = json.load(f)
                create_and_run_coletor(config)
            
            shutil.rmtree(f"configs/temp_{hash}")
        
if __name__ == "__main__":
    PAGES = {
        "Generalização de Configuração de Coleta": app1,
        "Criação de coletores": app2
    }
    
    st.sidebar.title('Escolha uma opção')
    selection = st.sidebar.radio('',list(PAGES.keys()))
    page = PAGES[selection]
   
    
    if selection == 'Generalização de Configuração de Coleta':
        page()
    elif selection == 'Criação de coletores':
        page()