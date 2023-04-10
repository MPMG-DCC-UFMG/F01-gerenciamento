import pandas as pd
from github import Github
from zenhub import Zenhub

import figures as fig_module
import extract_data
import utils
from transform_data import *

import spacy
nlp = spacy.load('pt_core_news_sm')

#TODO move to transform_data
def main_tranform_data(repo, creators):
    
    list_municipios = utils.loader_data(column_name='municipio', path_to_read='data/municipios.csv')
    info_issues = extract_data.get_all_issues(repo, creators)
    df = pd.DataFrame(info_issues)
    
    df['lower_title'] = df['title'].str.lower()
    df = filter_(df, column_name='lower_title')

    results = fill_cities(df, nlp, list_municipios)
    municipios_df = pd.DataFrame(results, index=[0]).T.reset_index()
    
    df = df.merge(municipios_df, left_on='title', right_on='index')[[
        'title', 'number', 'created_at', 'closed_at', 'labels', 'state', 0]]
    df = df.rename(columns ={0: 'municipio'})
    df['municipio'] = df['municipio'].str.strip()
    
    df = filter_by_labels(df)    
    
    # TODO Error format_date(line 39) if we remove
    df.to_csv("data/df.csv", index=False)
    df = pd.read_csv("data/df.csv")
    
    df['closed_at'] = df['closed_at'].fillna(0)
    df = format_date(df, time_column='closed_at', status='closed')
    df = format_date(df, time_column='created_at', status='created')    

    closed_df = issues_matrix(df, state_column='closed', time_column='format_date_closed')
    open_df = issues_matrix(df, state_column='open', time_column='format_date_created')
    
    columns_name = sort_columns(open_df)
        
    open_df = open_df[columns_name]
    try:
        closed_df = closed_df[columns_name]
    except:
        closed_df[columns_name[-1]] = [0]*len(closed_df)
        closed_df = closed_df[columns_name]
        
    date_columns = columns_name[1:]
    
    open_df[date_columns] = open_df[date_columns].astype(int)
    closed_df[date_columns] = closed_df[date_columns].astype(int)
    
    closed_df = fill_gaps(open_df, closed_df)
    closed_df = closed_df.sort_values('municipio')
    open_df = open_df.sort_values('municipio')

    df['week'] =  pd.to_datetime(df['closed_at']).dt.strftime('%W')
    
    return df, open_df, closed_df

def update_data_coletas(git_token, zh_token, closed_column='closed', open_column='open'):    
    
    """
    Atualiza os dados das coletas. 
    Tempo estimado: ~5min (incluindo espera automática, devido a limites de requisições ao ZenHub)
    """
    
    repo_id='357557193'    
    zh = Zenhub(zh_token)
    g = Github(git_token)
    
    repo_C01 = g.get_repo("MPMG-DCC-UFMG/C01")
    repo_F01 = g.get_repo("MPMG-DCC-UFMG/F01")
    
    creators = ['carbo6ufmg', 'RitaRez', 'asafeclemente', 'CinthiaS', 'isabel-elise', 'albertoueda', 
                'arthurnader', 'GabrielLimab', 'lucas-maia-96', 'dalila20', 'AntonioNvs','GabiAraujo',
                'rafaelmg7','jorgesilva2407']
    
    df, open_df, closed_df = main_tranform_data(repo_C01, creators)
    open_df.to_csv("data/open_df.csv", index=False)
    closed_df.to_csv("data/closed_df.csv", index=False)

    count_month = count_by_month(open_df, closed_df)
    count_month.to_csv("data/count_month.csv", index=False)
    
    week_status = count_by_week(df, time_column='closed_at')
    week_status.to_csv('data/week_status.csv', index=False)    
    df.to_csv("data/df.csv", index=False)
       
    issues_epic_df, epics_id = count_issues_epic(df, zh, repo_F01, repo_id)
    aux = pd.DataFrame([['Habeas Data','Licitação', 4.0, 0.0]], columns=['template','tag','closed', 'open'])
    issues_epic_df = pd.concat([issues_epic_df, aux])
    issues_epic_df.to_csv("data/issues_epic_df.csv", index=False)

    epics_info, count_epics_month, count_epics_week = summarize_epics(epics_id, repo_F01)
    count_epics_month.to_csv("data/count_epics_month.csv", index=False) 
    count_epics_week.to_csv("data/count_epics_week.csv", index=False) 
    epics_info.to_csv("data/epics.csv", index=False) 

    df_tags = count_by_tags(issues_epic_df)
    df_tags.to_csv("data/df_tags.csv", index=False)    

    epics_info = pd.read_csv("data/epics.csv")
    top_templates = pd.read_csv("data/top_templates.csv")    
    subtags = pd.read_csv("data/tags_epics.csv").subtag.to_list()
    tags = process_epics_for_tags(epics_info, top_templates, subtags)
    tags.to_csv('data/tags_epics.csv', index_label='subtag')
   

def update_data_desenvolvimento(git_token, zh_token, closed_column='closed', open_column='open'):    
    """
    Atualiza os dados do desenvolvimento
    """        
    repo_id='357557193'    
    zh = Zenhub(zh_token)
    g = Github(git_token)
    repo_F01 = g.get_repo("MPMG-DCC-UFMG/F01")
    
    epics_id = extract_data.get_epics_ids(zh, repo_id)
    epics_df = extract_data.get_info_filtered_issues(epics_id, repo_F01)
    epics_df.to_csv('data/epics_dev.csv', index=False)
    
    tags = pd.read_csv('data/tags_epics.csv', index_col='subtag')
    status_dev = process_status_validacao(tags, epics_df)
    status_dev.to_csv('data/status_dev.csv')
