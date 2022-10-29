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

    #TODO check if necessary
    # fig.add_trace(go.Histogram(
    #     histfunc='sum',
    #     y=count_month[y1_column],
    #     x = x_column,
    #     cumulative_enabled=cumulative_enabled,
    #     name=name1,
    #     marker_color='#F03C33'))
    
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

def plot_speed_epics(df, title):     
            
    # Medindo velocidade atual
    velocidade_total = df["closed"].mean()          
    df["closed_cumsum"] = df["closed"].cumsum()
    velocidade_coleta = df["Coletado"].mean()       
    velocidade_mes_anterior = df["Coletado"][:-1].mean()          
    df["coletado_cumsum"] = df["Coletado"].cumsum()         
    df["naocoletado_cumsum"] = df["Não coletável"].cumsum()   

    df = df.merge( pd.DataFrame(["11/2021", "12/2021"] + [f'{x:02d}/2022' for x in range(1,13)] + 
                                ["01/2023", "02/2023"], columns=["month_year"]), how="right").fillna(0)       
    # Baselines
    n_templates = 15 + 5            # 15 + 5 municipios
    total_epics_by_template = 29    # Siplanweb    
    
    total_epics = total_epics_by_template * n_templates    
    total_months = df.shape[0]
    ideal_speed = total_epics / total_months
    
    media_nao_coletavel = (12 + 12 + 12 + 8) / 4   # Siplanweb + Betha + MunicipalNet + ADPM    
    total_coletaveis = total_epics - (media_nao_coletavel * n_templates)
    ideal_speed_discounted = total_coletaveis / total_months
            
    # Plot
    fig =  px.bar(df, x="month_year", y="coletado_cumsum", title=title, opacity=0.5, height=500, width=1000, #, "naocoletado_cumsum"
                 labels={"value":"Epics concluídas (acumulado)", "month_year":"Mês", 'variable':''})

    fig.update_layout(yaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 100))
    fig.add_traces([
        go.Scatter(x=df.month_year, y=[i * ideal_speed for i in range(1, total_months+1)], name="Planejado", opacity=1,
                  line=go.scatter.Line(color='#ef553b')), #color="red" ff6692 ef553b     
        go.Scatter(x=df.month_year, y=[i * ideal_speed_discounted for i in range(1, total_months+1)], name="Coletável",
                  line=go.scatter.Line(color="#00CC96")), #AB63FA
        go.Scatter(x=df.month_year, y=[i * velocidade_coleta for i in range(1, total_months+1)], name="Realizado",
                  line=go.scatter.Line(color="#636efa"), opacity=1),#, text=df), #8c86ff
        go.Scatter(x=df.month_year, y=[i * velocidade_mes_anterior for i in range(1, total_months+1)], name="Mês anterior",
                  line=go.scatter.Line(color="#636efa"), opacity=0.2),#, text=df), #8c86ff
        # go.Scatter(x=df.month_year, y=[i * velocidade_total for i in range(1, total_months+1)], name="Total Fechado",
        #           line=go.scatter.Line(color="blue"), opacity=0.1),
    ])
    
    return fig

def plot_status_epics_dev(df, title, y_column, x_column, hue, showlegend=True):    

    fig = px.imshow(
        df, height=1800, width=1700, title=title,
        color_continuous_scale=[(0, "green"), (0.25, 'lightgreen'), (0.5, "#64b5cd"), 
                                (0.75, '#FFD700'), (1, 'lightblue')]
    )     
        
    fig.update_traces(opacity=0.75)
    fig.update_xaxes(tickangle=-90, side="top")
    fig.update_yaxes(showgrid=True, gridwidth=5)
    
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Status", 
            tickvals=[1,2,3,4,5],
            ticktext=["Testado","Parametrizado","Implementado","Em Implementação",'Previsto'],
            lenmode="pixels", 
            len=200), 
        font=dict(size=20)
    )
    
    return fig

def plot_pre_coleta(df, title='Resultados da Sondagem Automática'):
    df = df.sort_index(axis=0)
    df = df.reindex(sorted(df.columns), axis=1)

    fig = px.imshow(
        df, height=900, width=800, title=title,
        # color_continuous_scale=[(0, "red"), (1, 'lightblue')]   # 2-state
        color_continuous_scale=[(0, "white"), (0.5, "red"), (1, 'lightblue')]  # 3-state
    )     
        
    fig.update_traces(opacity=0.75)
    fig.update_xaxes(tickangle=-90, side="top")
    fig.update_xaxes(showgrid=True, gridwidth=5)
    
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Subtag", 
            tickvals=[-1, 0, 1],
            ticktext=['Indeterminado', 'Não localizada', 'Localizada'],
            lenmode="pixels", 
            len=140), 
        font=dict(size=14)
    )
    
    return fig

def create_figures_coleta(closed_colum='closed', open_colum='open'):
    
    week_status = pd.read_csv('data/week_status.csv')    
    count_epics_month = pd.read_csv("data/count_epics_month.csv")    
    count_epics_week = pd.read_csv("data/count_epics_week.csv")              
    sondagem_df = pd.read_csv('data/resultados_templates.csv', index_col=0).astype(int)      
          
    epics_df = pd.read_csv("data/epics.csv")
    top_templates_df = pd.read_csv("data/top_templates.csv")
    open_df = pd.read_csv("data/open_df.csv")

    x = open_df.columns[1:].tolist()
    z = open_df.columns[1:]
    y = 'municipio'    

    return [
        plot_status_epics(epics_df, top_templates_df, sondagem_df),
        plot_speed_epics(count_epics_month, title='Coleta - Conclusão de Epics por Mês'),
        plot_status_week(
            week_status, title='Coletas fechadas por semana',
            y_column='closed_at', x_column='week', xaxis_title_text='Semanas'),
        plot_status_week(
            count_epics_week, title='Epics fechadas por semana',
            y_column='Coletado', x_column='week_year', xaxis_title_text='Semanas')
        # plot_status_mes(
        #     count_month, title='Coletas por mês',
        #     x_column=x, name1='Coletas a realizar', name2="Coletas realizadas",
        #     y1_column=open_colum, y2_column=closed_colum )
        # plot_stack(
        #     df_tags, title="Coletas por tag", x_column='tag', y2_column=open_colum, 
        #     y1_column=closed_colum, name2="Coletas a realizar", name1="Coletas realizadas", showlegend=False)
        # dropdown_stack(
        #     issues_epic_df, title="Coletas por template", 
        #     x_column='template', y2_column=open_colum, y1_column=closed_colum, 
        #     name2="Coletas a realizar", name1="Coletas realizadas", showlegend=False)
    ]

def create_figures_dev(closed_colum='closed', open_colum='open'):
    
    count_month = pd.read_csv("data/count_month_dev.csv")
    week_status = pd.read_csv('data/week_status_dev.csv')
    coletas_tag= pd.read_csv("data/coletas_tag_dev.csv")
    epics_dev_df= pd.read_csv("data/epics_dev.csv", index_col="template_rank")    
    
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
    
    #TODO for now, it simply uses the manually edited data/epics_dev.csv
    fig4 = plot_status_epics_dev(epics_dev_df, title='Visão Geral - Validadores feitos e a fazer',        
        y_column='template', x_column='title', hue="state")

    return fig1, fig2, fig3, fig4


def create_figures_automacao():
    
    s = pd.read_csv('data/resultados_templates.csv', index_col=0).astype(int)
    
    #NOTE correcao de erros nos nomes dos portais 
    # s = s.rename(index={
    #     'Porta Fácil (60)': 'Portal Facil (60)',
    #     'Porta Fácil (46)': 'Portal Fácil (46)',
    #     'Template 1 (22)': 'Template1 (22)',
    #     'Template 1 (9)': 'Template1 (9)',
    #     'Portla TP': 'Portal TP',
    # })
    # s.loc['GRP'] = -1

    fig1 = plot_pre_coleta(s, title='Resultados da Sondagem Automática (' + 
                    str(s.shape[0]) + ' templates x ' + str(s.shape[1]) + ' subtags )')

    return fig1

def plot_status_epics(df, top_templates_df, sondagem_df, title='Visão Geral - Epics por Template (Coletores feitos e a fazer)'):

    # resultados do buscador de subtags (sondagem)
    # templates_ja_analisados = ['ADPM', 'Betha', 'Municipal Net', 'Siplanweb', 'Memory']
    templates_ja_analisados = ['ADPM (22)', 'Betha (26)', 'Municipal Net (11)', 'Siplanweb (61)', 'Memory (66)']
    s = sondagem_df[sondagem_df == 0].count(axis=1)
    s = s[s != 0]
    s = s.drop(templates_ja_analisados)
    s = s.sort_index()
    nao_loc_autom = dict(s)
    
    # Fonte: Planilha Controle de Dados (#TODO transformar em Epics com "não-localizado")
    nao_loc_manual = {'Municipal Net (11)': 12}
    coletado_autom = {'Template2 (28)': 4}
    
    for template, count in nao_loc_autom.items():
        for i in range(count):
            df = df.append({'template':template, 'state':'Não coletável (autom.)', 'aux':1}, ignore_index=True)
            
    for template, count in nao_loc_manual.items():
        for i in range(count):
            df = df.append({'template':template, 'state':'Não coletável', 'aux':1}, ignore_index=True)
            
    for template, count in coletado_autom.items():
        for i in range(count):
            df = df.append({'template':template, 'state':'Coletado (autom.)', 'aux':1}, ignore_index=True)
       
    # Pre-process dataframes       
    count_col = 'aux'
    name_col  = 'template'
    top_templates_df = top_templates_df[top_templates_df['rank'] <= 15]
    df = top_templates_df.merge(df, how='left').fillna({'state':'Estimado', count_col:1})   
    templates = df['template'].dropna().unique() 
    
    # TODO usar arquivo separado
    total_ref = 29  # Siplanweb  
    total = dict.fromkeys(templates, total_ref)
    total['Betha (26)'] = 33
    total['ADPM (22)'] = 19
    total['PT (45)'] = 28
    total['Memory (66)'] = 23
    total['ABO (21)'] = 23
    
    # Fill missing (estimated) epics in df
    for template in templates:        
        created =  df.groupby('template').count()['state'][template]
        missing = total[template] - created
        size = df[df.template == template]['size'].values[0]
        name = df[df.template == template][name_col].values[0]

        for i in range(missing):            
            df = df.append({'template':template, 'state':'Estimado', name_col:name,
                            'size':size, count_col:1}, ignore_index=True)           
        
    df = df.sort_values(by=['state', 'template'], ascending=[True,False])
    xorder = df.groupby(['state', 'template']).count()['aux'][
        'Coletado'].sort_values(ascending=False).index.tolist()

    # Plot
    fig = px.bar(
        df, y=count_col, x=name_col, color='state', height=800, width=1100, title=title,
        color_discrete_map = {'Coletado':'green', 
                              'Coletado (autom.)':'#92d696', 
                              'Com bloqueio':'#9F2B68',
                              'Com epic criada':'#64b5cd', 
                              'Estimado':'lightblue', 
                              'Não coletável':'red', 
                              'Não coletável (autom.)':'#ff9e99'}, 
        labels = {count_col:"#Coletores", 
                  name_col:"Template / Município"}, opacity=0.75 )    
    
    fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':xorder})
    fig.update_xaxes(tickangle=45)
    fig.update_layout(font=dict(size=18))    
    
    return fig