import pandas as pd
import extract_data
import re

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

def string_to_datetime(x):
    
    try:
        return pd.to_datetime(x, format="%m/%Y")
    except:
        return pd.NaT
    
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
    found = re.match(r'.*"' + target_label + r'-([^"]*?)"', item_labels)    
    
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

def format_date(df, time_column, status):
    
    df['month'] = pd.DatetimeIndex(df[time_column]).month
    df['day'] = pd.DatetimeIndex(df[time_column]).day
    df['year'] = pd.DatetimeIndex(df[time_column]).year
    
    
    df['format_date_{}'.format(status)] = df['month'].astype(str) + '/' + df['year'].astype(str)
    
    return df

def count_by_week(df, column_to_group='week', time_column='closed_at'):
    
    df = df.loc[df['format_date_closed'] != "1/1970"]
    df = format_date(df, time_column='format_date_closed', status='closed')
    df[column_to_group] = df[column_to_group].astype(str)  + "/" + df['year'].astype(str)
    week_status = df.groupby([column_to_group]).count().reset_index()[[column_to_group, time_column]]
    new = week_status[column_to_group].str.split('/', expand=True)
    result = pd.concat([week_status, new], axis=1)
    week_status = result.sort_values([1, 0], ascending=[True, True])
    
    return week_status

def count_by_tags(df, list_tags, closed_colum='closed', open_column='open', tag_column='tag'):
    
    df_tags = df.groupby(tag_column).agg({open_column: 'sum', closed_colum: 'sum'}).reset_index()

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

def format_epics_data(epics_info, time_column, state):
    
    df = epics_info.loc[epics_info['state']==state]
    
    if state == 'closed':
        df[time_column] = df[time_column].fillna(0)

    df = format_date(df, time_column=time_column, status=state)
    df_count = df.groupby('format_date_{}'.format(state)).agg({'title': 'count'}).reset_index().rename(columns={'title': state, 'format_date_{}'.format(state): 'month'})
    
    return df, df_count


def process_epics(df, target_labels=['template', 'tag', 'subtag'], remove_orig_col=True):
    
    for target_label in target_labels:
        df[target_label] = df.apply(lambda x: find_label(x['labels'], target_label), axis=1)
        
    df.loc[df.labels.astype(str).str.contains('não-localizado'), 'state'] = 'Não localizado'
    df.loc[df.state == 'closed', 'state'] = 'Coletado'
    df.loc[df.state == 'open', 'state'] = 'Com epic criada'
    
    df = df.rename(columns={'number':'git_issue'})
    df['aux'] = 1 #TODO
    
    if remove_orig_col:
        df = df.drop(columns='labels')
    
    return df

def summarize_epics(epics_id, repo, info_issues, open_column='open', closed_column='closed'):
    
    epics = extract_data.get_issues_by_number(repo, numbers=epics_id)
    epics_info = pd.DataFrame(extract_data.get_issues_infos([epics], info_issues))
    epics_info = epics_info.loc[epics_info['title'].str.find("Coletor para o template") != -1]
    
    open_epics, count_open = format_epics_data(epics_info, time_column='created_at', state=open_column)
    closed_epics, count_closed = format_epics_data(epics_info, time_column='closed_at', state=closed_column)

    count_epics_month = count_open.merge(count_closed, on='month')
    count_epics_month['month'] = string_to_datetime(count_epics_month['month'])
    count_epics_month = count_epics_month.sort_values(by='month', ascending=True)
    count_epics_month['month'] = count_epics_month['month'].dt.strftime("%m/%Y").astype(str)
    
    epics_info = process_epics(epics_info)

    return epics_info, count_epics_month
     