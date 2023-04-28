import pandas as pd
from math import isnan
import logging
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

def plot_tags_coletadas(epics):
    
    n_templates_cobertos = epics[epics == 2].count(axis=1).values
    n_subtags_pendentes  = epics[epics == 0].count(axis=0).values

    y = [f'({n:02d}) {tag}' for n, tag in zip(n_templates_cobertos, epics.index)]
    x = [t for _, t in sorted(zip(n_subtags_pendentes, epics.columns))]

    tot_coletado = sum(n_templates_cobertos)
    tot_nao_coletavel = epics[epics == 1].count().sum()
    tot = len(x) * len(y)
    
    title = f'Subtags por Template<br><sup>{len(y)} subtags x {len(x)} templates '
    title += f'- Coletado: {tot_coletado} ({round( tot_coletado*100/tot , 1)}%) '
    title += f'- Não-Coletável: {tot_nao_coletavel} ({round( tot_nao_coletavel*100/tot , 1)}%)'
    title += f'- Fechado: {tot_coletado+tot_nao_coletavel} ({round( (tot_coletado+tot_nao_coletavel)*100/tot , 1)}%)</sup>'
    
    fig = px.imshow(
        epics[x], y=y, height=1150, width=800, title=title, 
        color_continuous_scale=[(0, '#B9E3C6'), (0.5, '#D81E5B'), (1, '#59C9A5')])     
        
    fig.update_traces(opacity=0.80)
    fig.update_xaxes(tickangle=-90, side="top")
    fig.update_yaxes(showgrid=True, gridwidth=2, side='right')
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Status", lenmode='pixels', len=90, x=1.2, y=0.95, 
            tickvals=[0,1,2],
            ticktext=['Previsto', 'Não coletável', 'Coletado']), 
        font=dict(size=12))
    
    fig.write_image('fig/tags.png', scale=3)    
    
    return fig

def plot_speed_epics(df, df_week, title):      
    
    df['coletado_cumsum'] = df['Coletado'].cumsum()   
    coletado_cumsum_anterior = df['coletado_cumsum'][:-1].values.tolist()
    total_coletado_mes_anterior  = df['Coletado'][:-1].sum()
    
    ritmo_atual     = df_week['Coletado'][-4:].sum()
    ritmo_anterior  = df_week['Coletado'][-8:-4].sum() # df['Coletado'][-2:-1].values[0]
    ritmo_historico = coletado_cumsum_anterior[-1] / (df.shape[0] - 1)
    logging.info(f'Epics coletáveis fechadas (atual/anterior/historico): {int(ritmo_atual)}/{int(ritmo_anterior)}/{int(ritmo_historico)}')

    # Meses de interesse
    df = df.merge( pd.DataFrame(["11/2021", "12/2021"] + [f'{x}/2022' for x in range(1,13)] + 
                                [f'{x}/2023' for x in range(1,8)], columns=["month_year"]), how="right").fillna(0)    
    
    # Referencias
    n_templates = 15 + 5           # 15 + 5 municipios
    total_epics_by_template = 24   # baseada em 19/20 templates + municipios
    media_nao_coletavel = 7        # baseado em 14/15 templates
    
    total_epics = total_epics_by_template * n_templates    
    total_months = df.shape[0]
    future_months = total_months - len(coletado_cumsum_anterior) + 1
    ideal_speed = total_epics / total_months
    
    total_coletaveis = total_epics - (media_nao_coletavel * n_templates)
    ideal_speed_discounted = total_coletaveis / total_months
    
    previsao_mes_anterior = [total_coletado_mes_anterior + (i * ritmo_anterior) for i in range(future_months)] # ritmo_historico|ritmo_anterior
    previsao_atual = [total_coletado_mes_anterior + (i * ritmo_atual) for i in range(future_months)]
    
    # Plot
    fig =  px.bar(df, x="month_year", y='coletado_cumsum', title=title, opacity=0.5, height=500, width=1000,
                 labels={"coletado_cumsum":"Epics concluídas", "month_year":"Mês", 'variable':''})

    fig.update_layout(
        yaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 100),
        legend = dict(x = 0.015, y = 0.97),
    )
    fig.add_traces([
        go.Scatter(x=df.month_year, y=[i * ideal_speed for i in range(1, total_months+1)], name="Planejado", opacity=1,
                   mode='lines+markers', line=go.scatter.Line(color='#ef553b')), #color="red" ff6692 ef553b     
        go.Scatter(x=df.month_year, y=[i * ideal_speed_discounted for i in range(1, total_months+1)], name="Coletável",
                   mode='lines+markers', line=go.scatter.Line(color="#00CC96")), #AB63FA
        go.Scatter(x=df.month_year, y=[i * ritmo_historico for i in range(1, total_months-future_months+2)], name="Realizado",  
                   opacity=1, line=go.scatter.Line(dash='solid', color="#636efa")), 
        go.Scatter(x=df.month_year[-future_months:], y=previsao_atual, name="Realizado", showlegend=False,
                   opacity=1, line=go.scatter.Line(dash='dot', color="#636efa")),
        go.Scatter(x=df.month_year[-future_months:], y=previsao_mes_anterior, name="Mês anterior",
                   opacity=0.3, line=go.scatter.Line(dash='dot', color="#636efa")),
    ])
    
    return fig

def plot_status_epics(df, top_templates, sondagem, title='Visão Geral - Epics por Template (Coletores feitos e a fazer)'):

    top_templates = top_templates[top_templates['rank'] <= 15]
    stats = top_templates.set_index('template').to_dict()
    total = stats['total_epics']
    
    # total nao coletavel (analise manual)
    total_nc = stats['total_nao_coletavel']
    total_nc = {a: int(b) for a,b in total_nc.items() if not isnan(b) }

    for template, count in total_nc.items():
        for i in range(count):
            df = df.append({'template':template, 'state':'Não coletável', 'aux':1}, ignore_index=True)
                
    # resultados de coletas e analises automaticas 
    coletado_autom = {'Template2 (28)': 3}  #4
    nao_loc_autom  = {}
    for template, count in nao_loc_autom.items():
        for i in range(count):
            df = df.append({'template':template, 'state':'Não coletável (autom.)', 'aux':1}, ignore_index=True)
    for template, count in coletado_autom.items():
        for i in range(count):
            df = df.append({'template':template, 'state':'Coletado (autom.)', 'aux':1}, ignore_index=True)
       
    # Pre-processing data
    count_col = 'aux'
    name_col  = 'shortname'
    df = top_templates.merge(df, how='left').fillna({'state':'Estimado', count_col:1})   
    templates = df['template'].dropna().unique()     
   
    # Fill missing (estimated) epics in df
    for template in templates:        
        created =  df.groupby('template').count()['state'][template]
        missing = total[template] - created
        size = df[df.template == template]['size'].values[0]
        name = df[df.template == template][name_col].values[0]

        for i in range(missing):            
            df = df.append({'template':template, 'state':'Estimado', name_col:name,
                            'size':size, count_col:1}, ignore_index=True)           

    # sorting x-axis
    df = df.sort_values(by=['state', name_col], ascending=[True,True])
    xorder = df.groupby(['state', name_col]).count()['aux']['Coletado']
    for x in df[name_col].unique():
        if x not in xorder: xorder[x] = 0
        
    xorder = xorder.sort_values(ascending=False).index.tolist()
    m = [x for x in xorder if x.startswith('(m')]
    xorder = [x for x in xorder if x not in m]
    xorder = xorder + m
    
    # Plot
    fig = px.bar(
        df, y=count_col, x=name_col, color='state', height=800, width=1100, title=title,
        color_discrete_map = { 'Coletado':'green', 'Coletado (autom.)':'#92d696', 
            'Com bloqueio':'#9F2B68', 'Com epic criada':'#64b5cd', 'Estimado':'lightblue', 
            'Não coletável':'red', 'Não coletável (autom.)':'#ff9e99'}, 
        labels = {count_col:"#Coletores", name_col:"Template / Município"}, 
        opacity = 0.75 )    
    
    fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':xorder}, font=dict(size=18))
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_figures_coleta(closed_colum='closed', open_colum='open'):
    
    week_status = pd.read_csv('data/week_status.csv')    
    count_epics_month = pd.read_csv("data/count_epics_month.csv")    
    count_epics_week = pd.read_csv("data/count_epics_week.csv")      
    count_month = pd.read_csv("data/count_month.csv")              
    sondagem_df = pd.read_csv('data/resultados_templates.csv', index_col=0).astype(int)      
          
    epics_df = pd.read_csv("data/epics.csv")
    top_templates_df = pd.read_csv("data/top_templates.csv")
    open_df = pd.read_csv("data/open_df.csv")

    x = open_df.columns[1:].tolist()

    return [
        plot_status_epics(epics_df, top_templates_df, sondagem_df),
        plot_speed_epics(
            count_epics_month, count_epics_week, title='Coleta - Conclusão de Epics por Mês'),
        plot_status_week(
            week_status, title='Coletas fechadas por semana',
            y_column='closed_at', x_column='week_year', xaxis_title_text='Semanas'),
        plot_status_week(
            count_epics_week, title='Epics fechadas por semana',
            y_column='Coletado', x_column='week_year', xaxis_title_text='Semanas'),
        plot_status_mes(
            count_month, title='Coletas por mês',
            x_column=x, name1='Coletas a realizar', name2="Coletas realizadas",
            y1_column='open', y2_column='closed' )
    ]

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

def plot_status_validacao(df):
    
    n_temp_wip  = df[df != 0].count(axis=1)
    n_temp_done = df[df == 4].count(axis=1).to_dict()
    n_subt_wip  = df[df != 0].count(axis=0)
    
    # Sorting rows an columns
    y_order = [s for _, s in sorted(zip(n_temp_wip, n_temp_wip.index), reverse=True)]    
    y_labels = [f'({ n_temp_done[s] :02d}) {s}' for s in y_order]
    df = df.reindex(y_order)   
    x_order = [t for _, t in sorted(zip(n_subt_wip, n_subt_wip.index), reverse=True)]
    
    tot_validado = sum(list(n_temp_done.values()))
    tot_nao_coletavel = df[df == 1].count().sum()
    tot = len(x_order) * len(y_order)
    concluido = tot_validado + tot_nao_coletavel
    title = f'Validadores por Template/Subtag<br>'
    title += f'<sup>{len(y_order)} subtags x {len(x_order)} templates: 800 (100%)'
    title += f' - Validado: {tot_validado} ({round( tot_validado*100/tot , 1)}%)'
    title += f' - Não coletável: {tot_nao_coletavel} ({round( tot_nao_coletavel*100/tot , 1)}%)'
    title += f' - Concluído: {concluido} ({round( (concluido)*100/tot , 1)}%)</sup>'
    
    fig = px.imshow(
        df[x_order], y=y_labels, height=1150, width=800, title=title, 
        labels={'y':'subtags (#validadores testados)', 'x':'templates'},
        color_continuous_scale=[(0, '#DDFCD9'), (0.25, '#F45B69'), (0.5, '#59C9A5'), 
                                (0.75, '#028EA1'), (1, '#156079')])
        # https://coolors.co/114b5f-028090-e4fde1-456990-f45b69
        
    # fig.update_traces(opacity=0.90)
    fig.update_xaxes(tickangle=-90, side="top")
    fig.update_yaxes(showgrid=True, gridwidth=2, side='right')
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Status", lenmode='pixels', len=150, x=1.3, y=0.94, 
            tickvals=[0,1,2,3,4],
            ticktext=['Previsto', 'Não coletável', 'Coletado', 'Validação em progresso', 'Validado']), 
        font=dict(size=12))
    
    fig.write_image('fig/status-dev.png', scale=3)    
    
    return fig

def create_figures_dev(closed_colum='closed', open_colum='open'):
    
    count_month  = pd.read_csv("data/count_month_dev.csv")
    week_status  = pd.read_csv('data/week_status_dev.csv')
    coletas_tag  = pd.read_csv("data/coletas_tag_dev.csv")   
    tags         = pd.read_csv('data/tags_epics.csv', index_col='subtag')
    status_dev   = pd.read_csv('data/status_dev.csv', index_col='subtag')
    open_df      = pd.read_csv("data/open_df_dev.csv")

    x = open_df.columns[1:].tolist()
    
    return [
        plot_status_validacao(status_dev),  
        plot_tags_coletadas(tags),
        plot_status_mes(
            count_month, x_column=x, name1='Issues abertas', name2="Issues fechadas",
            y1_column=open_colum, y2_column=closed_colum, title='Generalizações por mês'),    
        plot_status_week(
            week_status, y_column='closed_at', x_column='week',
            title='Testes de generalização feitos por semana', xaxis_title_text='Semanas'),
        dropdown_stack(
            coletas_tag, title="Generalizações por template", x_column='template', y2_column=open_colum,
            y1_column=closed_colum, name2="Issues fechadas", name1="Issues abertas", showlegend=False),
    ]


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

def create_figures_automacao():
    
    s = pd.read_csv('data/resultados_templates.csv', index_col=0).astype(int)
    fig1 = plot_pre_coleta(s, title='Resultados da Sondagem Automática (' + 
                    str(s.shape[0]) + ' templates x ' + str(s.shape[1]) + ' subtags )')

    return fig1
