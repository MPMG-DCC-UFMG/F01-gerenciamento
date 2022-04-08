import pandas as pd

def loader_data(column_name, path_to_read='data/municipios.csv'):
    
    df = pd.read_csv(path_to_read)
    df['count_words'] = df[column_name].str.split(" ").apply(lambda x: len(x))
    result = list(df.sort_values('count_words', ascending=False)[column_name])
    
    return result