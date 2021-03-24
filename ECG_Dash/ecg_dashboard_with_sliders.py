# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import dash_table as dt

import pandas as pd
import plotly.graph_objects as go

# Bootstrap:
body = dbc.Container([
        dbc.Row([
             dbc.Col([
                dcc.Markdown(''' 
                        
                        > ### Dashboard for ECG Waveform
                        
                    '''
                , style={"background-color": "lightsteelblue"})
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.H5("Select offset in hours")
            ]),
        ]),
        dbc.Row([
                dbc.Col(
                    [
                        html.Div([
                           dcc.Slider(
                            id='hour-offset',
                            min=0,
                            max=23,
                            value=0,
                            step = 1,
                        ),
                            
                        ]),
                    ]), # Col1
            ]),
         dbc.Row([
            dbc.Col([
                html.H5("Select interval in minutes")
            ]),
        ]),
        dbc.Row([
                dbc.Col([
                        html.Div([
                            
                            dcc.Slider(
                            id='minute-offset',
                            min=0,
                            max=59,
                            value=0,
                            marks = {str(i):{'label': str(i), 'style': {"transform": "rotate(270deg)"}} for i in range(0,60)},
                            step = None,
                        ),
                        ]),
                        html.Div(id='intermediate-value', style={'display': 'none'})
                ]), # Col1
             ], align = "center"),
         dbc.Row([
            dbc.Col([
                html.Div(id='display-selected-values')
            ]) # Col1
         ], align = "center"), # Row 2
         dbc.Row([
            dbc.Col([
                html.Hr(),
            ]),
            dbc.Col([
                html.Hr(),
            ]),
         ]), # Row 3
         dbc.Row([
            dbc.Col([
                html.Div([
                        dcc.Graph(id='waveform-graphic'),
                    ]), 

             ]), # Col1
        ]),
         dbc.Row([
             dbc.Col([
                 html.Div(id="update-table"),
             ]) # Col1
        ], align = "top") # Row 4 - "align" unneeded if 'top'.  Other choices include "center" etc.
    ])


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#df = pd.read_json("http://localhost:8000/api/data/0/1/yes", orient="split")

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


app.layout = html.Div([body])


@app.callback(
    Output('intermediate-value', 'children'),
    Input('hour-offset', 'value'),
    Input('minute-offset', 'value'))
def clean_data(selected_hour, selected_minutes):
    # filtered_df = df[df.year == selected_year]
    url = f"http://localhost:8000/api/data/{selected_hour}/{selected_minutes}/yes"
    df = pd.read_json(url, orient="split")
    json_data = df.to_json(date_format='iso', orient='split')
    return json_data 

@app.callback(
    Output('waveform-graphic', 'figure'),
    Input('intermediate-value', 'children'))
def set_waveform_figure(jsonified_cleaned_data):
    dff = pd.read_json(jsonified_cleaned_data, orient='split')
    fig = px.line(dff, x='wallclock', y="values")
#     fig = px.line(dff, x="wallclock", y="values")
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20),
                      xaxis = dict(type='date'), transition_duration=500)

    return fig

@app.callback(
    Output('update-table', 'children'),
    Input('intermediate-value', 'children'))
def update_table_output(jsonified_cleaned_data):
    dff = pd.read_json(jsonified_cleaned_data, orient='split')

    return html.Div(
        [
            dt.DataTable(
                data=dff.to_dict("rows"),
                columns=[{"id": x, "name": x} for x in dff.columns],
                page_size=10
            )
        ]
    )
@app.callback(
    Output('display-selected-values', 'children'),
    Input('hour-offset', 'value'),
    Input('minute-offset', 'value'))
def set_display_children(selected_hour, selected_minutes):
    return u'{}:{} is the selected hour and minutes offset'.format(
        selected_hour, selected_minutes,
    )
if __name__ == '__main__':
    app.run_server(debug=True)
