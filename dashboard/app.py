# -*- coding: utf-8 -*-
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import logging

import figures
import main_etl

# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#F9F9F9",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

def html_div_chart(fig):
    return html.Div([ 
        html.Div([ dcc.Graph(figure=fig) ],
        className="pretty_container 6 columns",)], 
        className="row flex-display",)

def coleta_layout():
        
    count_month = pd.read_csv("data/count_month.csv")    
    open_df = pd.read_csv("data/open_df.csv")

    count_open = count_month['open'].sum()
    count_closed = count_month['closed'].sum()
    municipios_cobertos = len(open_df['municipio'].tolist())

    week_status = pd.read_csv('data/week_status.csv')
    count_coletas_semana = week_status[-1:]['closed_at'].values[0]

    epics = pd.read_csv('data/count_epics_month.csv')
    
    count_closed_epics = epics['closed'].sum().astype(int)
    count_coletado_epics = epics['Coletado'].sum().astype(int)
    
    #NOTE estimativas baseada em 13 templates
    count_total_epics = 25 * 20   
    count_total_coletavel = count_total_epics - (7 * 20)

    figs = figures.create_figures_coleta()
      
    # Create app layout
    layout = html.Div(
        [
            dcc.Store(id="aggregate_data"),
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
            html.Div([ html.Div([ html.Div([
                html.H3("F01 - Coletas",style={"margin-bottom": "0px"},),
                html.H5( "", style={"margin-top": "0px"} ), ])], className="two-half column", id="title",),
                    html.Div([   
                            html.Button("Atualizar Dados", id="refresh-button"),
                            html.Div(id='output-container-button', children=None),
                        ], className="one-third column", id="button-git", ), ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "25px"},),

            # Estatisticas
            html.Div([ html.Div( [ html.Div([
        
                html.Div([
                    html.H6(id="coletas_fechadas"), 
                    html.P('Coletas concluídas na semana: {}'.format(count_coletas_semana)),
                    html.P('Coletas concluídas no total / abertas: {} / {}'.format(count_closed, count_open)),
                    html.P('Municípios relacionados: {}'.format(municipios_cobertos))
                ], id="div-coletas_fechadas", className="mini_container",),

                html.Div([
                    html.H6(id="tags"), 
                    html.P('Epics concluídas (total): {} / {} ({:.1f}%)'.format(
                        count_closed_epics, count_total_epics, 
                        100*count_closed_epics/count_total_epics,)), 
                    html.P("Epics concluídas (coletável): {} / {} ({:.1f}%)".format(
                        count_coletado_epics, count_total_coletavel, 
                        100*count_coletado_epics/count_total_coletavel))
                ], id="div-tags", className="mini_container",),

            ], id="info-container", className="row container-display",), 
            ], id="right-column", className="12 columns", ), ], className="row flex-display",),

            # Graficos
            html_div_chart(figs[0]),
            html_div_chart(figs[1]),
            html_div_chart(figs[2]),
            html_div_chart(figs[3]),
            html_div_chart(figs[4]),
        
        ], id="mainContainer", style={"display": "flex", "flex-direction": "column"},
    )
    
    return layout


def desenvolvimento_layout():
    
    figs =  figures.create_figures_dev()
      
    # Create app layout
    layout = html.Div(
        [
            dcc.Store(id="aggregate_data"),
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
            html.Div([         
        
                html.Div([ html.Div([        
                    html.H3("F01 - Validação",style={"margin-bottom": "0px"},),
                    html.H5( "", style={"margin-top": "0px"} ),
                ])], className="two-half column", id="title", ),

                html.Div([           
                    html.Button("Atualizar Dados", id="refresh-button"),
                    html.Div(id='output-container-button', children=None),
                ], className="one-third column", id="button-git", ), 

            ], id="header", className="row flex-display", style={"margin-bottom": "25px"},) ,
            
            # Graficos
            html_div_chart(figs[0]),
            html_div_chart(figs[1]),
            html_div_chart(figs[2]),
            html_div_chart(figs[3]),
            html_div_chart(figs[4]),

        ], id="mainContainer", style={"display": "flex", "flex-direction": "column"},
    )
    
    return layout


def automacao_layout():
    
    fig1 = figures.create_figures_automacao()
      
    # Create app layout
    layout = html.Div([
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div([ 
            html.Div([ 
                html.Div([
                    html.H3("F01 - Automação",style={"margin-bottom": "0px"},),
                    html.H5( "", style={"margin-top": "0px"} ),])
                ], className="two-half column", id="title", 
            ),
        ], id="header", className="row flex-display", style={"margin-bottom": "25px"},),
        
        html.Div([ html.Div([
            dcc.Graph(id="graph4", figure=fig1)], 
            className="pretty_container 6 columns",)], className="row flex-display",
        ),            

    ], id="mainContainer",  style={"display": "flex", "flex-direction": "column"},)
    
    return layout

#---------------------------------------------------------------------------------------------

app = Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], 
                external_stylesheets=[dbc.themes.BOOTSTRAP])

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')


sidebar = html.Div(
    [
        html.Img(
            src=app.get_asset_url("logo.png"),
            id="plotly-image",
            style={
                "height": "80px",
                "width": "auto",
                "margin-bottom": "25px",
            },
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Coleta", href="/", active="exact"),
                dbc.NavLink("Validação", href="/validacao", active="exact"),
                dbc.NavLink("Automação", href="/automacao", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

app.title = "F01 - Coletas"
server = app.server

layout = dict(
        autosize=True,
        automargin=True,
        margin=dict(l=30, r=30, b=20, t=40),
        hovermode="closest",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend=dict(font=dict(size=10), orientation="h")
    )
#app.layout = create_layout

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])

@app.callback(Output('output-container-button', 'children'), Input("refresh-button", "n_clicks"))
def refresh(n_clicks):

    if n_clicks is None:
        raise PreventUpdate
    else:        
        main_etl.update_data_coletas(git_token, zh_token)
        main_etl.update_data_desenvolvimento(git_token, zh_token)
        html.A(href='/')

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):

    if pathname == "/":
        logging.info('Renderizando layout de coleta...')
        layout = coleta_layout()
        return layout

    elif pathname == "/validacao":
        logging.info('Renderizando layout de desenvolvimento...')
        layout = desenvolvimento_layout()
        return layout

    elif pathname == "/automacao":
        logging.info('Renderizando layout de automação...')
        layout = automacao_layout()
        return layout
    
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )        

# Repository credentials 
# Expects a file 'tokens.txt' with exact two lines: gh token then zh token
# Note: remember to gitignore this file to avoid revoking the tokens
def read_auth_tokens(filename = 'tokens.txt'):    
    global git_token, zh_token    
    logging.info('Lendo tokens de autenticacao...')

    with open(filename) as f:
         git_token, zh_token = [line.rstrip('\n') for line in f.readlines()]    

if __name__ == '__main__':
    read_auth_tokens()
    app.run_server(port=8050)
    # To find the process PID: $ lsof -i :8050 #TODO get PID dinamically and display
    