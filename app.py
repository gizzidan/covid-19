# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# master dataframe
df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/03-24-2020.csv")
init_date = datetime.date(2020, 3, 24).strftime("%m-%d-%y%y")
df["Date"] = init_date
df = df.dropna()

prev_date = datetime.date(2020, 3, 24).strftime("%m-%d-%y%y")
current_date = datetime.date(2020, 3, 25).strftime("%m-%d-%y%y")

new = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv".format(current_date))
new["Date"] = current_date
df = df.append(new)
df = df.dropna()

prev_df = df[df["Date"].str.match(prev_date)]
current_df = df[df["Date"].str.match(current_date)]

# NJ
prev_nj = prev_df[prev_df['Province_State'].str.match('New Jersey')]
nj = current_df[current_df['Province_State'].str.match('New Jersey')]

total_confirmed = np.sum(nj["Confirmed"])
total_deaths = np.sum(nj["Deaths"])
total_recovered = np.sum(nj["Recovered"])
total_active = np.sum(nj["Active"])


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(children=[
    html.H1(
        children='NJ COVID-19 Dashboard',
        style={
            'textAlign': 'center',
           
        }
    ),
    html.P(
        style={
            'textAlign': 'center',
           
        },
        children="Daily updated dashboard of NJ COVID-19 Metrics. This is a work in progress..."
    ),
    html.Div(
        className="grid-three",
        style={
            'textAlign': 'center',
            
         },
        children=[
            html.Div( 
                className="big-metric",
                children=[
                    html.H3(
                        
                        children="Total Confirmed",
                        
                    ),
                    html.H2(
                        children=total_confirmed,
                       
                    ),
                ]
            ),
            html.Div( 
                className="big-metric",
                children=[
                    html.H3(
                        children="Total Deaths",
                        
                    ),
                    html.H2(
                        children=total_deaths,
                       
                    ),
                ]
            ),
             html.Div( 
                className="big-metric",
                children=[
                    html.H3(
                        children="Total Recovered",
                        
                    ),
                    html.H2(
                        children=total_recovered,
                       
                    ),
                ]
            )
        ]
    ),

    html.Div(
        className='footer',
        children=[
            'Built by Dan Gizzi using Dash, a web application framework for Python',
            html.Br(),
            'Data from COVID-19 Data Repository by Johns Hopkins CSSE'],
        
        style={
        'textAlign': 'center',
        'color': colors['text']
    }),

])

if __name__ == '__main__':
    app.run_server(debug=True)