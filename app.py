# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta
import requests
import os.path
import plotly
import plotly.express as px

app = dash.Dash(__name__)
app.title = 'COVID-19 NJ Dashboard'
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{%title%}</title>
        {%favicon%}
        {%css%}   
    </head>
    <body>
        {%app_entry%}
        <footer>
            <div class='footer'>
            <p>
            Built by Dan Gizzi using Dash, a web application framework for Python. 
            <br/>
            Data from COVID-19 Data Repository by Johns Hopkins CSSE.   
            </p>     
            </div>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# master dataframe
def load_csv(date_list, df):
    for x in date_list:
        print(df)
        li = []
        li.append(df)
        request = requests.get("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv".format(x))
        if request.status_code == 404:
            print('file does not exist yet')
            print(df)
            pass
        else:
            print('Adding new day')
            day = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv".format(x))
            init_date = x
            day["Date"] = init_date
            li.append(day)
            df = pd.concat(li, axis=0, ignore_index=True, sort=False)
            df.to_csv('./master_list.csv', index=False)
    return df
    
if os.path.exists('./master_list.csv'):
    print("master list already exists")
    df = pd.read_csv('./master_list.csv')
    df = df.sort_values(by=['Date'], ascending=False)
    print("Checking for new days")
    start = pd.to_datetime(df['Date'].iloc[0], format='%m-%d-%Y')
    today = datetime.datetime.today()
    dt = today - start
    date_list = [today - datetime.timedelta(days=x) for x in range(dt.days)]
    date_list = [x.strftime("%m-%d-%y%y") for x in date_list]
    print(date_list)
    df = load_csv(date_list, df)
    
else:
    print("building new master list")
    df = pd.DataFrame()
    start = date(2020, 1, 21)
    today = date.today() 
    dt = today - start
    date_list = [today - datetime.timedelta(days=x) for x in range(dt.days)]
    date_list = [x.strftime("%m-%d-%y%y") for x in date_list]
    print(date_list)
    df = load_csv(date_list, df)
    df.to_csv('./master_list.csv', index=False)



current_date = df.sort_values(by=['Date'], ascending=False)
current_date = current_date['Date'].iloc[0]

current_date = datetime.datetime.strptime(current_date,'%m-%d-%Y')
prev_date = current_date - datetime.timedelta(days=1)

current_date = current_date.strftime("%m-%d-%y%y")
prev_date = prev_date.strftime("%m-%d-%y%y")

prev_df = df[df["Date"].str.match(prev_date)].dropna(subset=['Province_State'])
current_df = df[df["Date"].str.match(current_date)].dropna(subset=['Province_State'])

# NJ
prev_nj = prev_df[prev_df['Province_State'].str.match('New Jersey')]
nj = current_df[current_df['Province_State'].str.match('New Jersey')]
nj = nj.rename(columns = {'Admin2':'County'})

def make_metric(df, column):
    metric = int(np.sum(df[column]))
    metric = f"{metric:,}"
    return metric

total_confirmed = make_metric(nj, "Confirmed")
total_deaths = make_metric(nj, "Deaths")
total_recovered = make_metric(nj, "Recovered")
total_active = make_metric(nj, "Active")

def sign(metric):
    output = ''
    current = np.sum(nj[metric])
    prev = np.sum(prev_nj[metric])
    abs_prev = abs(prev) 
    if abs_prev == 0:
        confirmed_change = 0.0
    else:
        confirmed_change = np.round((np.true_divide((current - prev), abs_prev) * 100),2)
    if confirmed_change > 0:
        sign = "+"
    elif confirmed_change == 0.0:
        sign = 'no change'
    else:
        sign = ""
    if sign == 'no change':
        output = "{}".format(sign)
    else:
        output = "{}{}%".format(sign,confirmed_change)
    return output

def color(pchange):
    if pchange[0] == '+':
        color = 'green'
    elif pchange[0] == '-':
        color = 'red'
    else:
        color = 'white'
    return color

all_nj = df.dropna(subset=['Province_State'])
all_nj = all_nj[all_nj['Province_State'].str.match('New Jersey')]
all_nj['Date'] = pd.to_datetime(all_nj['Date'], format='%m-%d-%Y')
all_nj = all_nj.set_index('Date')
all_nj['Year'] = all_nj.index.year
all_nj['Month'] = all_nj.index.month
all_nj['Weekday Name'] = all_nj.index.weekday_name

nj = nj.sort_values('County', ascending=True)
data=nj[['County', 'Confirmed', 'Deaths', 'Recovered', 'Active']].reset_index()

all_nj_daily = all_nj.groupby(['Date']).agg(['sum']).reset_index()
all_nj_daily = all_nj_daily[['FIPS','Date', 'Confirmed', 'Deaths', 'Recovered', 'Active']]

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}




app.layout = html.Div(className='main-container', children=[
    html.H1(
        children='NJ COVID-19 Dashboard',
        style={
            'textAlign': 'center',
            'paddingTop': '40px'
           
        }
    ),
    html.P(
        style={
            'textAlign': 'center',
            'fontSize': '24px',
           
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
                    html.H4(
                        className=color(sign("Confirmed")),
                        children=sign("Confirmed"),
                       
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
                    html.H4(
                        className=color(sign("Deaths")),
                        children=sign("Deaths"),
                       
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
                    html.H4(
                        className=color(sign("Recovered")),
                        children=sign("Recovered"),
                       
                    ),
                ]
            )
        ]
    ),
    html.Div(className='grid-two', children = [
        html.Div(className='section', children = [
            html.H3('Confirmed Cases Time Series'),
            dcc.Graph(figure=px.line(all_nj_daily, x="Date", y='Confirmed')),
        ]),
        html.Div(className='section', children = [
            html.H3('Compare metrics by County'),
            dcc.Dropdown(
                id='x', 
                options = [
                {'label': 'Confirmed Cases', 'value': 'Confirmed'},
                {'label': 'Deaths', 'value': 'Deaths'},
                {'label': 'Recovered', 'value': 'Recovered'},
            ], 
            value='Confirmed',
            searchable = False,
            clearable = False
         ),
            dcc.Graph(id='graph', figure=px.bar(data))
        ])
    ])

])

@app.callback(
    Output('graph', 'figure'), 
    [Input('x', 'value')])
def cb(x):
    return px.bar(data, y='County', x=x, color=x,
        hover_data=['County', 'Confirmed', 'Deaths', 'Recovered'],
        orientation='h', height=600).update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
if __name__ == '__main__':
    app.run_server(debug=True)
