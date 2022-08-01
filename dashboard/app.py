# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import math, pandas as pd, datetime as dt, sys
import plotly.io as pio
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


def coleta_layout():
    
    count_month = pd.read_csv("data/count_month.csv")
    df_tags = pd.read_csv("data/df_tags.csv")
    open_df = pd.read_csv("data/open_df.csv")

    count_open = count_month['open'].sum()
    count_closed = count_month['closed'].sum()
    municipios_cobertos = len(open_df['municipio'].tolist())

    week_status = pd.read_csv('data/week_status.csv')
    count_coletas_semana = week_status[-1:]['closed_at'].values[0]

    epics = pd.read_csv('data/count_epics_month.csv')
    
    #TODO this number should match:
    #https://github.com/MPMG-DCC-UFMG/F01/issues?page=4&q=label%3Aepic+sort%3Acreated-asc+label%3A%22Realiza%C3%A7%C3%A3o+F01%22+is%3Aclosed
    count_closed_epics = epics['closed'].sum()
    count_total_epics = 29 * 20  #NOTE estimado via Siplanweb

    #TODO fix if necessary
    count_tags = len(df_tags.loc[df_tags['closed'] != 0]['closed'])

    fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10 = figures.create_figures_coleta()
      
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
                        html.Button("Refresh Data", id="refresh-button"),
                        html.Div(id='output-container-button', children=None),
                        #html.A(html.Button('Refresh Page'),href='/'),                           
                        ],
                        className="one-third column",
                        id="button-git",
                    ),
                ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),

            # Resumo
            html.Div([ html.Div( [ html.Div([
                html.Div(
                    [html.H6(id="tags"), html.P("Coletas concluídas (semana): {}".format(count_coletas_semana))],
                    id="div-tags", className="mini_container",),
                html.Div(
                    [html.H6(id="coletas_fechadas"), html.P("Coletas concluídas / Total: {} / {}".format(
                        count_closed, count_open))], id="div-coletas_fechadas", className="mini_container",),
                html.Div(
                    [html.H6(id="tags"), html.P("Epics / Total: {} / {} ({:.1f}%)".format(
                        count_closed_epics, count_total_epics, 100*count_closed_epics/count_total_epics))],
                    id="div-tags", className="mini_container",),
                html.Div(
                    [html.H6(id="municipios"), html.P("Municípios relacionados: {}".format(municipios_cobertos))],
                    id="div-municipios", className="mini_container"),                    

            ], id="info-container", className="row container-display",), 
            ], id="right-column", className="12 columns", ), ], className="row flex-display",),

            # Graficos
            html.Div([ html.Div([dcc.Graph(
                id="graph9", figure=fig9)], className="pretty_container 6 columns",)], className="row flex-display",),
            html.Div([ html.Div([dcc.Graph(
                id="graph10", figure=fig10)], className="pretty_container 6 columns",)], className="row flex-display",),
            html.Div([ html.Div([dcc.Graph(
                id="graph6", figure=fig6)], className="pretty_container 6 columns",) ], className="row flex-display",),
            html.Div([ html.Div([dcc.Graph(
                id="graph1", figure=fig1)], className="pretty_container 6 columns",) ],className="row flex-display", ),
            html.Div([ html.Div([dcc.Graph(
                id="graph7", figure=fig7)], className="pretty_container 6 columns",) ], className="row flex-display",),
            html.Div([ html.Div([dcc.Graph(
                id="graph3", figure=fig3)], className="pretty_container 6 columns",) ], className="row flex-display",),
  
            #NOTE not being used 
            # html.Div([ html.Div([dcc.Graph(
            #     id="graph2", figure=fig2)], className="pretty_container 6 columns",) ], className="row flex-display",),
            # html.Div([ html.Div([dcc.Graph(
            #     id="graph4", figure=fig4)],className="pretty_container six columns",)],className="row flex-display",),
            # html.Div([ html.Div([dcc.Graph(
            #     id="graph5", figure=fig5)],className="pretty_container six columns",)],className="row flex-display",),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )
    
    return layout


def desenvolvimento_layout():
    
    fig1, fig2, fig3, fig4 =  figures.create_figures_dev()
      
    # Create app layout
    layout = html.Div(
        [
            dcc.Store(id="aggregate_data"),
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3("F01 - Validação",style={"margin-bottom": "0px"},),
                                    html.H5( "", style={"margin-top": "0px"} ),
                                ]
                            )
                        ],
                        className="two-half column",
                        id="title",
                    ),
                    html.Div(
                        [   
                            html.Button("Refresh Data", id="refresh-button"),
                            html.Div(id='output-container-button', children=None),

                        ],
                        className="one-third column",
                        id="button-git",
                    ),
                   
                ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),
            
            html.Div(
                [
                    html.Div([dcc.Graph(id="graph4", figure=fig4)], className="pretty_container 6 columns",)
                ],
                className="row flex-display",
            ),            
            html.Div(
                [
                    html.Div([dcc.Graph(id="graph1", figure=fig1)], className="pretty_container 6 columns",)
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div([dcc.Graph(id="graph2", figure=fig2)], className="pretty_container 6 columns",)
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div([dcc.Graph(id="graph3", figure=fig3)], className="pretty_container 6 columns",)
                ],
                className="row flex-display",
            ),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )
    
    return layout


def automacao_layout():
    
    fig1 = figures.create_figures_automacao()
      
    # Create app layout
    layout = html.Div([
            dcc.Store(id="aggregate_data"),
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
            html.Div([ html.Div([ html.Div( [
                
                html.H3("F01 - Automação",style={"margin-bottom": "0px"},),
                
                html.H5( "", style={"margin-top": "0px"} ),] ) ],  
                    className="two-half column", id="title", ),
                    html.Div( [   
                        html.Button("Refresh Data", id="refresh-button"),
                        html.Div(id='output-container-button', children=None), ],
                        className="one-third column", id="button-git",
                    ), ], id="header", className="row flex-display",
                style={"margin-bottom": "25px"},
            ),
            
            html.Div([ html.Div([
                dcc.Graph(id="graph4", figure=fig1)], 
                className="pretty_container 6 columns",)], className="row flex-display",
            ),            
        
        ], id="mainContainer",  style={"display": "flex", "flex-direction": "column"},
    )
    
    return layout

#---------------------------------------------------------------------------------------------

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], 
                external_stylesheets=[dbc.themes.BOOTSTRAP])

sidebar = html.Div(
    [
        html.Img(src=app.get_asset_url("logo.png"),
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
        raise dash.exceptions.PreventUpdate
    else:        
        app.logger.info('Atualizando dados de coletas...')
        main_etl.update_data_coletas(git_token, zh_token)
        
        #TODO automatizar (#8)
        # app.logger.info('Atualizando dados de desenvolvimento...')
        # main_etl.update_data_desenvolvimento(git_token, zh_token)
        
        app.logger.info('Dados atualizados.')
        html.A(href='/')
        
        
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):

    if pathname == "/":
        app.logger.info('Renderizando layout de coleta...')
        layout = coleta_layout()
        return layout

    elif pathname == "/validacao":
        app.logger.info('Renderizando layout de desenvolvimento...')
        layout = desenvolvimento_layout()
        return layout

    elif pathname == "/automacao":
        app.logger.info('Renderizando layout de automação...')
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

    app.logger.info('Lendo tokens de autenticacao...')

    with open(filename) as f:
         git_token, zh_token = [line.rstrip('\n') for line in f.readlines()]    


if __name__ == '__main__':
    read_auth_tokens()
    app.run_server(port=8050)
    # To find the process PID: $ lsof -i :8050 #TODO get PID dinamically and display
    