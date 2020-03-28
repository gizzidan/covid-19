# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta
import requests
import os.path
import plotly

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
            Built by Dan Gizzi using Dash, a web application framework for Python. 
            <br/>
            Data from COVID-19 Data Repository by Johns Hopkins CSSE.        
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
        li = []
        li.append(df)
        request = requests.get("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv".format(x))
        if request.status_code == 404:
            pass
        else:
            day = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv".format(x))
            init_date = x
            day["Date"] = init_date
            li.append(day)
            df = pd.concat(li, axis=0, ignore_index=True, sort=False)
    return df
    
if os.path.exists('./master_list.csv'):
    print("master list already exists")
    df = pd.read_csv('./master_list.csv')
    df = df.sort_values(by=['Date'], ascending=False)
    if df['Date'].iloc[0] == date.today().strftime("%m-%d-%y%y"):
        print("All up to date")
        pass
    else:
        print("Adding new days")
        df['Date'] = pd.to_datetime(df['Date'], format='%m-%d-%Y')
        print("date changed to datetime")
        start = pd.to_datetime(df['Date'].iloc[0], format='%m-%d-%Y')
        today = datetime.datetime.today()
        dt = today - start
        date_list = [today - datetime.timedelta(days=x) for x in range(dt.days)]
        date_list = [x.strftime("%m-%d-%y%y") for x in date_list]
        print(date_list)
        df['Date'] = df['Date'].dt.strftime("%m-%d-%y%y")
        df = load_csv(date_list, df)
        df.to_csv('master_list.csv')
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
    df.to_csv('master_list.csv')

current_date = df.sort_values(by=['Date'], ascending=False)
current_date = current_date['Date'].iloc[0]

current_date = datetime.datetime.strptime(current_date,'%m-%d-%Y')
prev_date = current_date - datetime.timedelta(days=1)

current_date = current_date.strftime("%m-%d-%y%y")
prev_date = prev_date.strftime("%m-%d-%y%y")

prev_df = df[df["Date"].str.match(prev_date)].dropna(subset=['Province_State']).dropna(axis='columns')
current_df = df[df["Date"].str.match(current_date)].dropna(subset=['Province_State']).dropna(axis='columns')

# NJ
prev_nj = prev_df[prev_df['Province_State'].str.match('New Jersey')]
nj = current_df[current_df['Province_State'].str.match('New Jersey')]

total_confirmed = np.sum(nj["Confirmed"])
total_deaths = np.sum(nj["Deaths"])
total_recovered = np.sum(nj["Recovered"])
total_active = np.sum(nj["Active"])


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

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}




app.layout = html.Div(children=[
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

])

if __name__ == '__main__':
    app.run_server(debug=True)
