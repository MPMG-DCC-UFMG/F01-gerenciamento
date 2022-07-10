import pandas as pd
import requests
import time
from zenhub import APILimitError

def get_epics_ids(zh, repo_id):
   
    try: 
        epics = zh.get_epics(repo_id).get('epic_issues')

    except APILimitError:  # tenta apenas mais uma vez
        print('Limite de requisicoes alcancado (ZenHub). Aguardando um minuto..')        
        time.sleep(60)
        epics = zh.get_epics(repo_id).get('epic_issues')

    epics_ids = [i.get('issue_number') for i in epics]

    return epics_ids

def get_data_epics(zh, epics_id, repo_id):
    
    issues_data = {} 

    for i in epics_id:
        try:
            issues_data[i] = zh.get_epic_data(repo_id=repo_id, epic_id=i) 

        except APILimitError:  # tenta apenas mais uma vez
            print('Limite de requisicoes alcancado (ZenHub). Aguardando um minuto..')        
            time.sleep(60)
            issues_data[i] = zh.get_epic_data(repo_id=repo_id, epic_id=i)  
        
    return issues_data

def get_pipeline_name(zh, repo_id_c01, issue_number, workspace_id='615dcc142f7e9b000f3b1fed'):

    try:
        issue = zh.get_issue_data(repo_id_c01, issue_number=issue_number)

    except APILimitError:  # tenta apenas mais uma vez
        print('Limite de requisicoes alcancado (ZenHub). Aguardando um minuto..')        
        time.sleep(60)
        issue = zh.get_issue_data(repo_id_c01, issue_number=issue_number)
        
    pipeline_name = [i.get('name') for i in issue.get('pipelines') if i.get('workspace_id') == workspace_id]
    
    return pipeline_name

def get_epics_info(repo_F01, issues_data):
    
    epics_info = {}
    for j in issues_data.keys():

        aux = {'issues': []}
        labels = load_labels(repo_F01, epic_id=j)
        
        template = get_specific_labels(labels, pattern='template')

        if template != None:
             
            aux['template'] = template
            aux['tag'] = get_specific_labels(labels, pattern='tag')
        
            dev = get_specific_labels(labels, pattern='development')

            for i in issues_data[j]['issues']:
                aux['issues'].append(i['issue_number'])
            
            epics_info[j] = aux
        
    return epics_info

def get_specific_labels(labels, pattern='tag'):
    
    label = next((s for s in labels if pattern in s), None) 
    
    if label != None:
        return label.split('-')[-1]
    return None

def load_labels(repo_F01, epic_id):
    
    labels = repo_F01.get_issue(epic_id).labels
    labels = [i.name for i in labels]
    
    return labels

def get_issues_by_creator(repo, creators, state='open'):
    
    issues = [repo.get_issues(creator=creator, state=state)  for creator in creators]
    
    return issues

def get_issues_by_number(repo, numbers):
    
    issues = [repo.get_issue(number=number) for number in numbers]
    
    return issues

def get_issues(repo, state='open'):
    
    issues = [repo.get_issues(state=state)]
    
    return issues

def get_issues_infos(all_issues, info_issues):
    #TODO refactor: info_issues only increases, mixed epics and other issues 

    for i in all_issues:
        for issue in i:
            info_issues['title'].append(issue.title)
            info_issues['number'].append(issue.number)
            info_issues['created_at'].append(issue.created_at)
            info_issues['labels'].append(issue.labels)
            info_issues['closed_at'].append(issue.closed_at)
            info_issues['state'].append(issue.state)
            
    return info_issues

def get_info_filtered_issues(epics_id, repo, filter_by='generalization test'):
    
    data = {'title': [], 'id':[] , 'tag':[], 'template': [], 'status': []}

    for epic_id in epics_id:
    
        issue = repo.get_issue(epic_id)
        labels = issue.labels
        labels = [i.name for i in labels]
    
        if filter_by in labels:

            data['title'].append(issue.title)
            data['id'].append(epic_id)
            data['tag'].append(get_specific_labels(labels, pattern='tag'))
            data['template'].append(get_specific_labels(labels, pattern='template'))
            data['status'].append(issue.state)
        
    df = pd.DataFrame(data)
    
    return df

def get_info_issues_by_id(ids, repo):
    
    data = {'title': [], 'id':[], 'status': [], 'created_at':[], 'closed_at':[]}
    
    for issue_id in ids:
    
        issue = repo.get_issue(issue_id)
    
        data['title'].append(issue.title)
        data['id'].append(issue_id)
        data['status'].append(issue.state)
        data['created_at'].append(issue.created_at)
        data['closed_at'].append(issue.closed_at)
        
    df = pd.DataFrame(data)
    
    return df

def fill_pipeline_array(df, pipeline_name):
    
    tam = len(df)
    diff = tam - len(pipeline_name)
    
    for i in range(diff):
        pipeline_name.append(None)
        
    df['pipeline_name'] = pipeline_name
    
    return df

def get_all_issues(repo, creators, info_issues):
    
    all_open_issues = get_issues_by_creator(repo, creators, state='open')
    info_issues = get_issues_infos(all_open_issues, info_issues) 
    
    all_closed_issues = get_issues_by_creator(repo, creators, state='closed')
    info_issues = get_issues_infos(all_closed_issues, info_issues) 

    df = pd.DataFrame(info_issues)

    return df


def print_zenhub_api_usage(zh_token, repo_id):
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "User-Agent": "ZenHub Python Client", })
    session.headers.update({"X-Authentication-Token": zh_token})

    response = session.get(url='https://api.zenhub.com/p1/repositories/' + repo_id + '/epics/1')
    
    headers = dict(response.headers)    
    used  = headers['X-RateLimit-Used']
    total = headers['X-RateLimit-Limit']
        
    print('Requisicoes ao Zenhub feitas por minuto / Limite: %s/%s' % (used, total))

