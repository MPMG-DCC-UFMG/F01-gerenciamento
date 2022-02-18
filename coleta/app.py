# -*- coding: utf-8 -*-

import pandas as pd
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.io as pio

import figures
import main_etl

def create_layout():
    
    count_month = pd.read_csv("data/count_month.csv")
    df_tags = pd.read_csv("data/df_tags.csv")
    open_df = pd.read_csv("data/open_df.csv")

    count_open = count_month['open'].sum()
    count_closed = count_month['closed'].sum()
    municipios_cobertos = len(open_df['municipio'].tolist())
    count_tags = len(df_tags.loc[df_tags['closed'] != 0]['closed'])

    fig1, fig2, fig3, fig4, fig5, fig6, fig7 = figures.main_create_figures()
      
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
                            html.Img(
                                src=app.get_asset_url("logo.png"),
                                id="plotly-image",
                                style={
                                    "height": "80px",
                                    "width": "auto",
                                    "margin-bottom": "25px",
                                },
                            )
                        ],
                        className="one-third column",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3("F01 - Coletas",style={"margin-bottom": "0px"},),
                                    html.H5( "", style={"margin-top": "0px"} ),
                                ]
                            )
                        ],
                        className="one-half column",
                        id="title",
                    ),
                    html.Div(
                        [   
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
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [html.H6(id="municipios"), html.P("Municípios Cobertos: {}".format(municipios_cobertos))],
                                        id="div-municipios",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="tags"), html.P("Tags Cobertas: {}".format(count_tags))],
                                        id="div-tags",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="coletas_fechadas"), html.P("Coletas Fechadas: {}".format(count_closed))],
                                        id="div-coletas_fechadas",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="coletas_abertas"), html.P("Coletas Abertas: {}".format(count_open))],
                                        id="div-coletas_abertas",
                                        className="mini_container",
                                    ),
                                 
                                ],
                                id="info-container",
                                className="row container-display",
                            ),
                            html.Div([
                                dcc.Graph(id="graph1", figure=fig1)],id="countGraphContainer",className="pretty_container",
                            ),
                        ],
                        id="right-column",
                        className="12 columns",
                    ),
                ],
                className="row flex-display",
            ),
             html.Div(
                [
                    html.Div([dcc.Graph(id="graph6", figure=fig6)], className="pretty_container 6 columns",)
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
                    html.Div([dcc.Graph(id="graph7", figure=fig7)],className="pretty_container 6 columns",),
                ],
                className="row flex-display",
            ),
            
            html.Div(
                [
                    html.Div([dcc.Graph(id="graph3", figure=fig3)], className="pretty_container 12 columns",),
                ],
                className="row flex-display",
            ),
  
            html.Div(
                [
                    html.Div([dcc.Graph(id="graph4", figure=fig4)],className="pretty_container six columns",),
                    html.Div([dcc.Graph(id="graph5", figure=fig5)],className="pretty_container six columns",),
                ],
                className="row flex-display",
            ),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )
    
    return layout

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],)

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

app.layout = create_layout

@app.callback(Output('output-container-button', 'children'), Input("refresh-button", "n_clicks"))
def refresh(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    else:
        main_etl.job()
        html.A(href='/')
        

if __name__ == '__main__':
    app.run_server(port=8050)

    

    