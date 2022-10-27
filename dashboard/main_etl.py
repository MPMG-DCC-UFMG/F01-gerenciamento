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

#TODO move to transform_data
def main_tranform_data(repo, creators):
    
    list_municipios = utils.loader_data(column_name='municipio', path_to_read='data/municipios.csv')
    list_items = utils.loader_data(column_name='tag', path_to_read='data/itens.csv')
    
    info_issues = extract_data.get_all_issues(repo, creators)
    df = pd.DataFrame(info_issues)
    
    df['lower_title'] = df['title'].str.lower()
    df = transform_data.filter_(df, column_name='lower_title')

    results = transform_data.fill_cities(df, nlp, list_municipios)
    municipios_df = pd.DataFrame(results, index=[0]).T.reset_index()
    
    df = df.merge(municipios_df, left_on='title', right_on='index')[[
        'title', 'number', 'created_at', 'closed_at', 'labels', 'state', 0]]
    df = df.rename(columns ={0: 'municipio'})
    df['municipio'] = df['municipio'].str.strip()
    
    df = transform_data.filter_by_labels(df)    
    
    # TODO Error format_date(line 39) if we remove
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

    count_month = transform_data.count_by_month(open_df, closed_df)
    count_month.to_csv("data/count_month.csv", index=False)
    
    df['week'] =  pd.to_datetime(df['closed_at']).dt.strftime('%W')
    week_status = transform_data.count_by_week(df, column_to_group='week', time_column='closed_at')
    week_status.to_csv('data/week_status.csv', index=False)    
    df.to_csv("data/df.csv", index=False)
       
    issues_epic_df, epics_id = transform_data.count_issues_epic(df, zh, repo_F01, repo_id)
    aux = pd.DataFrame([['Habeas Data','Licitação', 4.0, 0.0]], columns=['template','tag','closed', 'open'])
    issues_epic_df = pd.concat([issues_epic_df, aux])
    issues_epic_df.to_csv("data/issues_epic_df.csv", index=False)

    epics_info, count_epics_month, count_epics_week = transform_data.summarize_epics(epics_id, repo_F01)
    count_epics_month.to_csv("data/count_epics_month.csv", index=False) 
    count_epics_week.to_csv("data/count_epics_week.csv", index=False) 
    epics_info.to_csv("data/epics.csv", index=False) 

    df_tags = transform_data.count_by_tags(issues_epic_df)
    df_tags.to_csv("data/df_tags.csv", index=False)    
    
def update_data_desenvolvimento(git_token, zh_token, closed_column='closed', open_column='open'):
    
    """
    Atualiza os dados do desenvolvimento
    """
    
    repo_id='357557193'    
    zh = Zenhub(zh_token)
    g = Github(git_token)
    
    repo_C01 = g.get_repo("MPMG-DCC-UFMG/C01")
    repo_F01 = g.get_repo("MPMG-DCC-UFMG/F01")
    
    epics_id = extract_data.get_epics_ids(zh, repo_id)
    epics_df = extract_data.get_info_filtered_issues(epics_id, repo_F01)

    epics_id_dev = list(epics_df['id'])
    issues_data = extract_data.get_data_epics(zh, epics_id_dev, repo_id)
    epics_info = extract_data.get_epics_info(repo_F01, issues_data)
    epics_info_df = pd.DataFrame(epics_info).T.reset_index()

    exploded_df = epics_info_df.explode('issues').reset_index(drop=True)

    exploded_df = exploded_df.loc[~exploded_df['issues'].isna()]
    issues_id = exploded_df['issues'].tolist()

    info_issues_dev = extract_data.get_info_issues_by_id(issues_id, repo_F01)

    info_issues_dev.to_csv("data/info_issues_dev.csv", index=False)
    info_issues_dev = pd.read_csv("data/info_issues_dev.csv")

    info_issues_dev['closed_at'] = info_issues_dev['closed_at'].fillna(0)
    info_issues_dev = transform_data.format_date(info_issues_dev, time_column='closed_at', status='closed')
    info_issues_dev = transform_data.format_date(info_issues_dev, time_column='created_at', status='created')
    
    info_issues_dev['week'] =  pd.to_datetime(info_issues_dev['closed_at']).dt.strftime('%W')
    week_status = transform_data.count_by_week(info_issues_dev, column_to_group='week', time_column='closed_at')

    closed_df = info_issues_dev.pivot_table(
        values='title', index=['id'], columns='format_date_closed', aggfunc='count').fillna(0).reset_index()
    closed_df.drop('1/1970', axis = 1,inplace=True)

    open_df = info_issues_dev.pivot_table(
        values='title', index=['id'], columns='format_date_created', aggfunc='count').fillna(0).reset_index()

    columns_name = transform_data.sort_columns(open_df)
    open_df = open_df[columns_name]

    columns_name = transform_data.sort_columns(closed_df)
    closed_df = closed_df[columns_name]

    count_month_dev = transform_data.count_by_month(open_df, closed_df)

    df = info_issues_dev.merge(exploded_df, left_on='id', right_on='issues')
    df = df.groupby(['template','tag', 'status'])['status'].count().unstack().reset_index().fillna(0)
    df = df.sort_values('closed', ascending=False)

    count_month_dev.to_csv("data/count_month_dev.csv", index=False)
    open_df.to_csv("data/open_df_dev.csv", index=False)
    closed_df.to_csv("data/closed_df_dev.csv", index=False)
    df.to_csv("data/coletas_tag_dev.csv", index=False)
    week_status.to_csv('data/week_status_dev.csv', index=False)
