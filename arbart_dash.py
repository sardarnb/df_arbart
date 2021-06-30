import dash
import dash_table
import pandas as pd
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output, State

from pymongo import MongoClient

#import json
mongo_con_str = 'mongodb+srv://admin:1kFEJ9LQurPaIhhv@cluster0.cryeu.gcp.mongodb.net/test?authSource=admin&replicaSet=atlas-59dkal-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true&ssl_cert_reqs=CERT_NONE'


app = dash.Dash(__name__)

server = app.server

app.layout = dbc.Container([
    html.H1('Arb finder - Bart'),
    html.H3('View Golf Matchups between BT and BM'),
    dbc.Button('Refresh', id='refresh-match-table'),
    dbc.Spinner(html.Div(id='match_table_show')),
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000 * 5,  # in milliseconds
        n_intervals=0
    )
])


@app.callback(
    Output('match_table_show','children'),
    [Input('refresh-match-table','n_clicks'),
    Input('interval-component', 'n_intervals'),
     ])
def show_matches(x, y):
    client = MongoClient(mongo_con_str)
    mydb = client.bart
    collection = mydb.golf

    max_datetime = mydb.golf.find().sort("log_time", -1).limit(1)
    for latest_insert in max_datetime:
        latest_log_time = latest_insert['log_time']
    db_recs = mydb.golf.find({'log_time': latest_log_time})
    df_matchups = pd.DataFrame(list(db_recs))
    # df_matchups = pd.read_csv(r'https://raw.githubusercontent.com/sardarnb/df_arbart/main/df_arbart.csv')
    df = df_matchups[['match_time_bm', 'away_player', 'home_player', 'best_away','best_book_away', 'best_home','best_book_home', 'cum_prob',
            'cum_prob_spread','best_spread_away','best_spread_home','best_book_away_spread','best_book_home_spread', 'tournament_flg',
             'log_time']]
    df.log_time = pd.to_datetime(df.log_time)
    df = df.drop_duplicates()
    df.best_home = round(df.best_home, 2)
    df.best_away = round(df.best_away, 2)
    df.best_spread_away = round(df.best_spread_away, 2)
    df.best_spread_home = round(df.best_spread_home, 2)
    df.cum_prob = round(df.cum_prob, 2)
    df.cum_prob_spread = round(df.cum_prob_spread, 2)
    # df.loc[df.log_time == df.log_time.max()]
    data = df.loc[df.log_time == df.log_time.max()].to_dict('records'),
    m_table = dt.DataTable(
        id='match_table',
        columns=[{'name': 'match_time_bm', 'id': 'match_time_bm'},
                 {'name': 'away_player', 'id': 'away_player'},
                 {'name': 'home_player', 'id': 'home_player'},
                 {'name': 'best_away', 'id': 'best_away'},
                 {'name': 'best_home', 'id': 'best_home'},
                 {'name': 'best_book_away', 'id': 'best_book_away'},
                 {'name': 'best_book_home', 'id': 'best_book_home'},
                 {'name': 'cum_prob', 'id': 'cum_prob'},
                 {'name': 'cum_prob_spread', 'id': 'cum_prob_spread'},
                 {'name': 'best_spread_away', 'id': 'best_spread_away'},
                 {'name': 'best_spread_home', 'id': 'best_spread_home'},
                 {'name': 'best_book_away_spread', 'id': 'best_book_away_spread'},
                 {'name': 'best_book_home_spread', 'id': 'best_book_home_spread'},
                 {'name': 'tournament_flg', 'id': 'tournament_flg'},
                 {'name': 'log_time', 'id': 'log_time'},
                 ],
        data=data[0],
        # row_selectable='single',
        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['away_player', 'home_player']
        ],
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        # style_cell={
        #     'overflow': 'hidden',
        #     'textOverflow': 'ellipsis',
        #     'maxWidth': 0
        # },
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        filter_action="native",
    )

    client.close()
    return m_table


if __name__ == '__main__':
    app.run_server(debug=True)
