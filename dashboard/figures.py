import pandas as pd
import plotly

import plotly.graph_objects as go 
import plotly.figure_factory as ff
import plotly.express as px


def dropdown_stack(df, title, x_column, y1_column, y2_column, name1=None, name2=None, showlegend=False):

    fig =  px.bar(df, x="template", y=["closed", "open"])

    fig.update_layout(barmode='stack')

    tag_list = pd.unique(df['tag']).tolist() 
    buttons = []
    
    buttons.append(dict(method = "restyle",
                args = [{'y': [df['closed'], df['open']], 'x': [df['template']]}],
                label = "Todas as tags"))
    
    for tag in tag_list:
        aux = df.loc[df['tag'] == tag]
    
        buttons.append(dict(method = "restyle",
                args = [{'y': [aux['closed'], aux['open']], 'x':[aux['template']]},],
                label = tag))
    
    fig.update_layout(autosize=True, title=title,
                  updatemenus=[dict(active=0,
                                    buttons=buttons)
                              ]) 

    fig.update_traces(opacity=0.75, showlegend=showlegend)
    
    return fig

def plot_stack(
    df, title, x_column, y1_column, y2_column, name1=None, name2=None, showlegend=False):

    fig = go.Figure(data=[
        go.Bar(name=name1, x=df[x_column], y=df[y1_column], marker_color='#3E79FA'),
        go.Bar(name=name2, x=df[x_column], y=df[y2_column], marker_color='#F03C33'),
    ])

    fig.update_traces(opacity=0.75, showlegend=showlegend)
    
    fig.update_layout(
        barmode='stack', autosize = True, title=title, legend=dict(orientation="h"))
    
    return fig

def stack_by_tag (df, y_column, title, tag_column='tag', template_column='template'):
    
    tag_list= pd.unique(df[tag_column])

    data = []
    for i in tag_list:
        aux = df.loc[df[tag_column] == i]
        data.append(go.Bar(name=i, x=df[template_column], y=aux[y_column]))

    fig = go.Figure(data)
    fig.update_traces(opacity=0.75, showlegend=True)
    fig.update_layout(
        barmode='stack', autosize=True, title=title, legend=dict(orientation="v"))
    
    return fig

def plot_status_mes(count_month, x_column, title, y1_column, y2_column, name1=None, name2=None, cumulative_enabled=True):
                    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        histfunc='sum',
        y=count_month[y1_column],
        x = x_column,
        cumulative_enabled=cumulative_enabled,
        name=name1,
        marker_color='#F03C33'))
    
    fig.add_trace(go.Histogram(
        histfunc='sum', y=count_month[y2_column], 
        x = x_column,
        cumulative_enabled=cumulative_enabled,
        name=name2,
        marker_color='#3E79FA'))
    
    fig.update_traces(opacity=0.70)
    
    fig.update_layout(
        barmode='overlay', bargap=0, autosize=True, title=title, legend=dict(orientation="h"))

    return fig

def plot_status_week(week_status, title, y_column, x_column, xaxis_title_text):

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y = week_status[y_column],
        x = week_status[x_column].astype(str) ,
        marker_color='#3E79FA'))
    
    fig.update_traces(opacity=0.70)
    
    fig.update_layout(
        xaxis_title_text=xaxis_title_text, bargap=0, autosize=True, title=title)

    return fig

def create_heatmap(df, x, y, z, title):
    
    z =  df[z].to_numpy()
    y = df[y].to_list()
    
    fig = ff.create_annotated_heatmap(
            z=z,
            x=x,
            y=y,
            showscale=True,
            hoverongaps=True,
            colorscale='Blues'
            )
    
    fig.update_layout(
        width=530, height=4000, autosize=True)
     
    fig['layout']['xaxis']['side'] = 'top'
  
    return fig

def create_barplot(df, title, x_column, y1_column, y2_column, name1=None, name2=None, showlegend=False):

    fig =  px.bar(df, y="template", x=["closed", "open"], )

    fig.update_layout(barmode='stack', xaxis={'categoryorder':'total ascending'})    
    fig.update_layout(autosize=True, title=title) 
    fig.update_traces(opacity=0.75, showlegend=showlegend)
    
    return fig

def plot_status_template(df, title, y_column, x_column, hue, showlegend=True):
     
    total = 29 #TODO Siplanweb
    templates = epics_df['template'].dropna().unique()
    
    for template in templates:
        created =  df.groupby('template').count()['title'][template]
        missing = total - created
        for i in range(missing):
            df = df.append({'template':template, 'state':'Estimado', 'aux':1}, ignore_index=True)    
        
    df = df.sort_values(by=[hue, x_column])

    fig =  px.bar(df, y=y_column, x="aux", orientation="h", color=hue, height=800, width=900,
        color_discrete_map={"Coletado":"green", "Com epic criada":"#64b5cd", 'Estimado':'lightblue', "Não localizado":"red"}, 
        labels={"aux":"#Coletores (total estimado pelo template Siplanweb)"} )    
    fig.update_layout(title=title) 
    fig.update_traces(opacity=0.75, showlegend=showlegend)
    # Seaborn colors  
    # ['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd']
    
    return fig

def create_figures_coleta(closed_colum='closed', open_colum='open'):
    
    count_month = pd.read_csv("data/count_month.csv")
    week_status = pd.read_csv('data/week_status.csv')
    
    count_epics_month = pd.read_csv("data/count_epics_month.csv")
                              
    issues_epic_df = pd.read_csv("data/issues_epic_df.csv")
    df_tags = pd.read_csv("data/df_tags.csv")
    df = pd.read_csv("data/df.csv")
    open_df = pd.read_csv("data/open_df.csv")
    closed_df= pd.read_csv("data/closed_df.csv")
    template_df= pd.read_csv("data/coletas_por_template.csv")

    x = open_df.columns[1:].tolist()
    z = open_df.columns[1:]
    y = 'municipio'
    
    
    fig1 = plot_status_mes(count_month, title='Coletas por mês',
        x_column=x, name1='Coletas a realizar', name2="Coletas realizadas",
        y1_column=open_colum, y2_column=closed_colum )
    
    fig2 = plot_status_mes(count_epics_month, title='Quantidade de templates cobertos por mês',
        x_column=count_epics_month['month'].tolist(), name1='Coletas a realizar',
        name2="Coletas realizadas", y1_column=open_colum, y2_column=closed_colum)
    
    fig6 = plot_status_week(week_status, title='Coletas fechadas por semana',
        y_column='closed_at', x_column='week',
        xaxis_title_text='Semanas')
                  
    fig7 = dropdown_stack(issues_epic_df, title="Coletas por template", 
        x_column='template', y2_column=open_colum, y1_column=closed_colum, 
        name2="Coletas a realizar", name1="Coletas realizadas", showlegend=False)
    
    fig3 = plot_stack(df_tags, title="Coletas por tag", 
            x_column='tag', y2_column=open_colum, y1_column=closed_colum,
            name2="Coletas a realizar", name1="Coletas realizadas", showlegend=False)
    
    fig4 = create_heatmap(open_df, x, y, z, "Coletas a realizar")
    
    fig5 = create_heatmap(closed_df, x, y, z, "Coletas realizadas")

    fig8 = create_barplot(issues_epic_df, title="Coletas por Template: Realizadas X Planejadas (com issue) X Estimadas",
        x_column='template', y2_column=open_colum, y1_column=closed_colum, 
        name2="Coletas a realizar", name1="Coletas realizadas", showlegend=False)
    
    fig9 = plot_status_template(template_df, title='Epics por Template - Coletores feitos e a fazer',        
        y_column='template', x_column='title', hue="state", showlegend=True)

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9

def create_figures_dev(closed_colum='closed', open_colum='open'):
    
    count_month = pd.read_csv("data/count_month_dev.csv")
    week_status = pd.read_csv('data/week_status_dev.csv')
    coletas_tag= pd.read_csv("data/coletas_tag_dev.csv")
    
    open_df = pd.read_csv("data/open_df_dev.csv")
    closed_df= pd.read_csv("data/closed_df_dev.csv")

    x = open_df.columns[1:].tolist()
    z = open_df.columns[1:]
    y = 'municipio'
    
    
    fig1 = plot_status_mes(
        count_month, x_column=x, name1='Issues abertas', name2="Issues fechadas",
        y1_column=open_colum, y2_column=closed_colum, title='Generalizações por mês')
    
    
    fig2 = plot_status_week(
        week_status, y_column='closed_at', x_column='week',
        title='Testes de generalização feitos por semana', xaxis_title_text='Semanas')
    
    fig3 = dropdown_stack(
        coletas_tag, title="Generalizações por template", x_column='template', y2_column=open_colum,
        y1_column=closed_colum, name2="Issues fechadas", name1="Issues abertas", showlegend=False)
    
       
    return fig1, fig2, fig3