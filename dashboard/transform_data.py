import pandas as pd
import extract_data
import re
import json

def count_issues_epic(info_issues, zh, repo_F01, repo_id_f01):
    
    epics_id = extract_data.get_epics_ids(zh, repo_id_f01)
    issues_data = extract_data.get_data_epics(zh, epics_id, repo_id_f01)
    epics_info = extract_data.get_epics_info(repo_F01, issues_data)

    epics_info_df = pd.DataFrame(epics_info).T.reset_index()
    exploded_df = epics_info_df.explode('issues').reset_index(drop=True)

    exploded_df = exploded_df.merge(info_issues, left_on='issues', right_on='number')
    df = exploded_df.groupby(['template','tag', 'state'])['state'].count().unstack().reset_index().fillna(0)
    df = df.sort_values('closed', ascending=False)
        
    return df, epics_id

def issues_matrix(df, state_column, time_column):
    
    issues_df = df.copy()
    
    issues_df = issues_df[['title','municipio', time_column]]
    pivot_df = issues_df.pivot_table(values='title', index=['municipio'], columns=time_column, aggfunc='count').fillna(0)
    pivot_df = pivot_df.reset_index(level=0)
    
    return pivot_df

def fill_cities(df, nlp, list_municipios):

  results = {}

  for idx, row in df.iterrows():

    doc = nlp(row['title'])
    entity = {}

    results[row['title']] = ""

    for ent in doc.ents:
      entity[ent.label_] = ent.text

    try:
      result = entity.get("LOC")
      results[row['title']] = result
    except KeyError:
      results[row['title']] = ""

  
  for key in results.keys():
    for i in list_municipios:
      if key.find(i) != -1:
        results[key] = i
        break

  return results

def fill_gaps(open_df, closed_df):
    
    for idx, row in open_df.iterrows():
        
        if not row['municipio'] in list(closed_df['municipio']):
            
            new_row = {}
            for i in list(open_df.columns[:]):
    
                if i == 'municipio':
                    new_row['municipio'] = row['municipio']
                else:
                    
                    new_row[int(i)] = 0
                    
            closed_df = closed_df.append(new_row, ignore_index=True)
            
    return closed_df

def filter_by_labels(df, label_column='labels', labels_filter=['bug']):
    
    labels = df[label_column].astype(str)
    labels = [re.findall(r'"\s*([^"]*?)\s*"', label) for label in labels]
    labels = [" ".join(label) for label in labels]
    df[label_column] = labels
    
    for i in labels_filter:
        df = df.loc[~df[label_column].str.contains(i)]
    
    return df

def find_label(item_labels, target_label):    
    
    item_labels = str(item_labels)
    found = re.match(r'.*"' + target_label + r' - ([^"]*?)"', item_labels)    
    
    if found: 
        return found.group(1)
    
    return None

def datetime_to_string(x):
    
    try:
        return x.strftime("%-m/%Y")
    except:
        return pd.NaT

def filter_(df, column_name, pattern='coleta'):
    
    df = df.loc[df[column_name].str.contains(pattern)]
    
    return df

def sort_columns(df, date_format="%m/%Y"):
    
    date = pd.Series(df.columns[1:])
    
    datetime = date.apply(string_to_datetime)
    new_columns = list(datetime.sort_values().apply(datetime_to_string))
    new_columns.insert(0, df.columns[0])
    
    return new_columns

def count_by_week(df, column_to_group='week', time_column='closed_at'):
    
    df = df.loc[df['format_date_closed'] != "1/1970"]
    df = format_date(df, time_column='format_date_closed', status='closed')
    df[column_to_group] = df[column_to_group].astype(str)  + "/" + df['year'].astype(str)
    week_status = df.groupby([column_to_group]).count().reset_index()[[column_to_group, time_column]]
    new = week_status[column_to_group].str.split('/', expand=True)
    result = pd.concat([week_status, new], axis=1)
    week_status = result.sort_values([1, 0], ascending=[True, True])
    
    return week_status

def count_by_tags(df, list_tags=None, closed_colum='closed', open_column='open', tag_column='tag'):
    
    df_tags = df.groupby(tag_column).agg({open_column: 'sum', closed_colum: 'sum'}).reset_index()

    # se list_tags for fornecido, acrescenta as tags faltantes, senao lista somente as tags existentes
    if list_tags:
        aux = pd.unique(df_tags[tag_column]).tolist()
        unused_tags = list(set(list_tags) - set(aux) )
        
        unused_tags = pd.DataFrame(
            {tag_column: unused_tags, open_column: [0]*len(unused_tags), closed_colum: [0]*len(unused_tags)})
        df_tags = pd.concat([df_tags, unused_tags])
        
    return df_tags

def count_by_month(open_df, closed_df, closed_colum='closed', open_column='open'):

    count_open= {i: open_df[i].sum() for i in list(open_df.columns[1:])} 
    count_close = {i: closed_df[i].sum() for i in list(closed_df.columns[1:])} 

    result = {}
    result[open_column] = count_open
    result[closed_colum] = count_close
    
    return pd.DataFrame(result)

# Manter sincronizado com labels do repositorio:
#   https://github.com/MPMG-DCC-UFMG/F01/labels
def expand_states(df, target_labels=['template', 'tag', 'subtag'], remove_orig_col=True):
    
    for target_label in target_labels:
        df[target_label] = df.apply(lambda x: find_label(x['labels'], target_label), axis=1)
        
    # NOTE todas epics com label 'não-*' estão sendo agrupadas como 'Não coletável'
    df.loc[df.labels.astype(str).str.contains('não-'), 'state'] = 'Não coletável'   
    
    df.loc[df.labels.astype(str).str.contains('bloqueada'), 'state'] = 'Com bloqueio'    
    df.loc[df.state == 'closed', 'state'] = 'Coletado'
    df.loc[df.state == 'open', 'state'] = 'Com epic criada'
    
    df = df.rename(columns={'number':'git_issue'})
    df['aux'] = 1
    
    if remove_orig_col:
        df = df.drop(columns='labels')
    
    return df
    
# municipios = build_municipios_clusters_df('data/clusters.d3.json', 'data/part-00000', 'data/cluster-template.csv')
def build_municipios_clusters_df(clusters_json_path, part_0000_path, cluster_template_path):
    with open(clusters_json_path, 'r') as f:
         clusters_json = json.loads(f.read())

    municipios = []
    for cluster in clusters_json['children']:
        for municipio in cluster['children']:
            new_row = [int(municipio['name']), int(cluster['name']), int(cluster['size']/10)]
            municipios.append(new_row) 
            
    municipios = pd.DataFrame(municipios, columns=['municipio_id', 'cluster_id', 'cluster_size'],
                            dtype=int)

    nomes_municipios = pd.read_csv(part_0000_path, names=['municipio_id', 'municipio'])
    nomes_municipios['municipio'] = nomes_municipios['municipio'].apply(lambda x: x.split('/')[-1][:-5])        
    municipios = municipios.merge(nomes_municipios, on='municipio_id', how='left')

    cluster_template = pd.read_csv(cluster_template_path)
    cluster_template['template_name_size'] = cluster_template.template + \
        ' (' + cluster_template.cluster_n_portais.astype(str) + ')' 
    municipios = municipios.merge(cluster_template, on='cluster_id', how='left')
    
    municipios = municipios.sort_values(['cluster_size', 'template_name_size', 'municipio'], 
                                        ascending=[False, True, True])
    municipios = municipios[['municipio_id', 'municipio', 'template_name_size', 'template', 
                             'cluster_id',	'cluster_size',	'cluster_rank', 'cluster_n_portais']]
    
    municipios.to_csv('data/municipios_clusters.csv', index=False)
    
    return municipios

def string_to_datetime(x, dateformat='%m/%Y'):
    
    try:
        return pd.to_datetime(x, format=dateformat)
    except:
        return pd.NaT
    
def format_date(df, time_column, status):
    df['day'] = pd.DatetimeIndex(df[time_column]).day
    df['month'] = pd.DatetimeIndex(df[time_column]).month
    df['year'] = pd.DatetimeIndex(df[time_column]).year    
    df['week'] = pd.DatetimeIndex(df[time_column]).isocalendar().week.values
    
    df['week_year'] = df['week'].astype(str) + '/' + df['year'].astype(str)    
    df['format_date_{}'.format(status)] = df['month'].astype(str) + '/' + df['year'].astype(str)
        
    return df

def count_closed_epics(epics):
    
    epics = epics[~epics.closed_at.isna()]
    epics = format_date(epics, 'closed_at', '')    
    epics = epics.rename(columns={'format_date_': 'month_year'})
        
    counts = {}
    
    for period in ['month', 'week']:
        
        count = epics.groupby([f'{period}_year','state']).agg({'git_issue': 'count'})
        count = count.reset_index()
        count = count.pivot(index=f'{period}_year', columns='state', values='git_issue')
        count = count.fillna(0)
        count['closed'] = count.sum(axis=1) 
        count = count.reset_index()        

        # sort by closing date
        count[period] = count[f'{period}_year'].apply(lambda x: int(x.split('/')[0]))
        count['year'] = count[f'{period}_year'].apply(lambda x: int(x.split('/')[1]))
        count = count.sort_values(['year', period])
        
        counts[period] = count
    
    return counts['month'], counts['week']

def summarize_epics(epics_id, repo):
    
    epics = extract_data.get_issues_by_number(repo, numbers=epics_id)
    epics = pd.DataFrame(extract_data.add_issues_info([epics]))   
    epics = epics.loc[epics['title'].str.find("Coletor para") != -1]
    epics = expand_states(epics)

    count_epics_month, count_epics_week = count_closed_epics(epics)
        
    return epics, count_epics_month, count_epics_week     
    