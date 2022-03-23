from github import Github
from github3 import login
import streamlit as st
import json
import time

with open("data/template_issue_coleta.txt", 'r') as f:
    template_issue_coleta = f.read()
    
with open("data/template_issue_generalizacao.txt", 'r') as f:
    template_issue_generalizacao = f.read()

def body_text_coleta(template_issue_coleta, data, tag):
    
    template_issue_coleta = template_issue_coleta.replace("<TAG>", tag)
    issues = {}

    for municipio, link in data.items():
        title = 'Coleta de {} - {}'.format(tag, municipio)
        issue = template_issue_coleta.replace("<MUNICIPIO>", municipio)
        issue = issue.replace("<LINK>", link)
        
        issues[title] = issue
     
    return issues

def body_text_generalizacao(template_issue_generalizacao, data, tag):
    
    template_issue = template_issue_generalizacao.replace("<TAG>", tag)
    issues = {}

    for municipio in data:
        title = 'Teste de generalizacao para a tag {} - {}'.format(tag, municipio)
        issue = template_issue_generalizacao.replace("<MUNICIPIO>", municipio)
        issue = issue.replace("<TAG>", tag)

        issues[title] = issue
     
    return issues
           
def main(template_issue_coleta, template_issue_generalizacao):
    
    user=""
    
    st.title("Gerador de Issues")
    
    tags = ["", "Forma pela qual se dá o acesso à informação", "Informações institucionais do municipio", "Receitas", 
            "Licitação", "Contratos", "Despesas", "Concursos Públicos", "Servidores", "Obras Públicas",
           "Terceiro Setor", "Diárias de viagem", "Orçamento" ]
    
    creators = ["", 'RitaRez', 'asafeclemente', 'CinthiaS', 'isabel-elise', 'arthurnader', 'GabrielLimaB', 'lucas-maia-96']

    git_token = st.text_input("Entre com sua Token do GitHub.")
    
    repo_name = st.text_input("Entre com o nome do repositório que você deseja criar a issue", value='MPMG-DCC-UFMG/C01')
    
    user = st.selectbox("Nome do usuário no github. (Essa informação será utilizada para te atribuir como responsável por essa issue.", options=creators)
    
    tag = st.text_input("Entre com a tag da solicitação.")
    
    tipo = st.selectbox("Qual o tipo de issue?", options=[ "", 'Coleta', 'Teste de generalização'])
      
    uploaded_file = st.file_uploader("Carregue o arquivo de configurações aqui")
    
    if uploaded_file is not None:
  
        data = json.load(uploaded_file)

        if tipo == "Coleta":
            issues = body_text_coleta(template_issue_coleta, data, tag)
        elif tipo == "Teste de generalização":
            issues = body_text_generalizacao(template_issue_generalizacao, data, tag)
            
    
    b1 = st.button('Show Issues', key=0)
    if b1:
        
        st.markdown("### Atenção humano, você está criando uma issue de {}!".format(tipo))
    
        
        logtxtbox = st.empty()
        logtxt = ''
       
    
        for title, body in issues.items():
        
            logtxt = logtxt +  "\n\n--------------------- \nTítulo da issue: " + title + "\n" + body
            logtxtbox.text_area("Conteúdo da Issue: ", logtxt, height=700)
        
    agree1 = st.checkbox('Você visualizou as issues que serão criadas? Claro, eu sou um exemplo de humano!', key=0)
    if agree1:
        agree2 = st.checkbox('Você concorda em criar as issues? Sim!')
        if agree2:
            b2 = st.button('Criar issues', key=0)
            if b2:
            
                #gh = login(token=str(git_token))
                
                g = Github(git_token)
                repo = g.get_repo(repo_name)

        
                for title, body in issues.items():
                     #result = gh.create_issue(title=title, body=body, repository=repo_name, owner=user, label=['bug'])
                    i = repo.create_issue(
                           title=title,
                           body=body,
                           assignee=user,
                        labels=[
                            repo.get_label("[T] Realização F01"), repo.get_label("[0] Coleta")
                        ]
                    )
            
                st.write('Great!, Issues Criadas')
    
if __name__ == "__main__":
    main(template_issue_coleta, template_issue_generalizacao)
