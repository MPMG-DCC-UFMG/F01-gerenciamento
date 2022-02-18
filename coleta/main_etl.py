import pandas as pd
import os
from github import Github
from zenhub import Zenhub

import figures as fig_module
import extract_data
import transform_data
import utils

import spacy
nlp = spacy.load('pt_core_news_sm')

def main_tranform_data(repo, creators, info_issues):
    
    list_municipios = utils.loader_data(column_name='municipio', path_to_read='data/municipios.csv')
    list_items = utils.loader_data(column_name='tag', path_to_read='data/itens.csv')
    
    df = extract_data.get_all_issues(repo, creators, info_issues)
    
    df['lower_title'] = df['title'].str.lower()
    df = transform_data.filter_(df, column_name='lower_title')

    results = transform_data.fill_cities(df, nlp, list_municipios)
    municipios_df = pd.DataFrame(results, index=[0]).T.reset_index()
    
    df = df.merge(municipios_df, left_on='title', right_on='index')[['title', 'number', 'created_at', 'closed_at', 'labels', 'state', 0]]
    df = df.rename(columns ={0: 'municipio'})
    df['municipio'] = df['municipio'].str.strip()
    
    df = transform_data.filter_by_labels(df)
    
    df.to_csv("data/df.csv", index=False)
    df = pd.read_csv("data/df.csv")
    
    df['closed_at'] = df['closed_at'].fillna(0)

    df = transform_data.format_date(df, time_column='closed_at', status='closed')
    df = transform_data.format_date(df, time_column='created_at', status='created')
    

    closed_df = transform_data.issues_matrix(df, state_column='closed', time_column='format_date_closed')
    open_df = transform_data.issues_matrix(df, state_column='open', time_column='format_date_created')
    
    columns_name = transform_data.sort_columns(open_df)
        
    open_df = open_df[columns_name]
    try:
        closed_df = closed_df[columns_name]
    except:
        closed_df[columns_name[-1]] = [0]*len(closed_df)
        closed_df = closed_df[columns_name]
        
    date_columns = columns_name[1:]
    
    open_df[date_columns] = open_df[date_columns].astype(int)
    closed_df[date_columns] = closed_df[date_columns].astype(int)
    
    closed_df = transform_data.fill_gaps(open_df, closed_df)

    closed_df = closed_df.sort_values('municipio')
    open_df = open_df.sort_values('municipio')
    
    return info_issues, df, open_df, closed_df

def job( closed_column='closed', open_column='open'):
    
    repo_id='357557193'
    git_token='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'
    zh_token='7e7139e708aa0c236190828bfe80da2e89fd7830d30c38655d87cd7ed4fc6bc5670181fd6167fcda'
    
    zh = Zenhub(zh_token)
    g = Github(git_token)
    
    repo_C01 = g.get_repo("MPMG-DCC-UFMG/C01")
    repo_F01 = g.get_repo("MPMG-DCC-UFMG/F01")
    
    info_issues = {'title': [], 'number': [], 'created_at': [], 'closed_at': [], 'labels' : [], 'state': [] }
    creators = ['carbo6ufmg', 'RitaRez', 'asafeclemente', 'CinthiaS', 'isabel-elise', 'arthurnader']
    
    list_tags = ['Acesso à informação', 'Informações institucionais', 'Receitas', 'Despesas', 'Licitação', 'Contratos', 'Terceiro Setor', 'Concursos Públicos', 'Obras públicas', 'Servidores Públicos']
    
    info_issues, df, open_df, closed_df = main_tranform_data(repo_C01, creators, info_issues)

    count_month = transform_data.count_by_month(open_df, closed_df)
    
    df['week'] =  pd.to_datetime(df['closed_at']).dt.strftime('%W')
    week_status = transform_data.count_by_week(df, column_to_group='week', time_column='closed_at')
       
    issues_epic_df, epics_id = transform_data.count_issues_epic(df, zh, repo_F01, repo_id)
    count_epics_month = transform_data.count_epics_by_month(epics_id, repo_F01, info_issues)
    
    df_tags = transform_data.count_by_tags(issues_epic_df, list_tags)
    
    df.to_csv("data/df.csv", index=False)

    count_month.to_csv("data/count_month.csv", index=False)
    week_status.to_csv('data/week_status.csv', index=False)
    
    aux = pd.DataFrame([['Habeas Data','Licitação', 4.0, 0.0]], columns=['template','tag','closed', 'open'])
    issues_epic_df = pd.concat([issues_epic_df, aux])
    issues_epic_df.to_csv("data/issues_epic_df.csv", index=False)
    count_epics_month.to_csv("data/count_epics_month.csv", index=False) 
    df_tags.to_csv("data/df_tags.csv", index=False)
    
    open_df.to_csv("data/open_df.csv", index=False)
    closed_df.to_csv("data/closed_df.csv", index=False)
