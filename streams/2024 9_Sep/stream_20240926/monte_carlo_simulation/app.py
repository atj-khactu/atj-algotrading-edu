from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import random
import pandas as pd
import plotly.express as px

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


app.layout = html.Div([
    html.H1('Monte Carlo Simulation App'),

    dbc.Label('Risk per Trade:'),
    dbc.Input(id='risk-per-trade', value=100),

    dbc.Label('Win Rate:'),
    dbc.Input(id='win-rate', value=0.5),

    dbc.Label('RRR:'),
    dbc.Input(id='rrr', value=2),

    dbc.Label('Num. of Trades:'),
    dbc.Input(id='num-trades', value=100),

    dbc.Label('Num. of Simulations:'),
    dbc.Input(id='num-simulations', value=10),

    dbc.Button('Submit', id='submit-btn', style={'float': 'right'}),

    html.Br(),

    html.Hr(),
    dcc.Loading(id='page-content')

], style={'margin-left': '5%', 'margin-right': '5%', 'margin-top': '20px'})


@app.callback(Output('page-content', 'children'),
              Input('submit-btn', 'n_clicks'),
              State('risk-per-trade', 'value'),
              State('win-rate', 'value'),
              State('rrr', 'value'),
              State('num-trades', 'value'),
              State('num-simulations', 'value'))
def serve_page(n_clicks, risk_per_trade, win_rate, rrr, num_trades, num_simulations):
    print(n_clicks, risk_per_trade, win_rate, rrr, num_trades, num_simulations)

    if n_clicks is None:
        return

    risk_per_trade = float(risk_per_trade)
    win_rate = float(win_rate)
    rrr = float(rrr)
    num_trades = int(num_trades)
    num_simulations = int(num_simulations)

    profit_list = []

    for simulation in range(num_simulations):
        for i in range(num_trades):
            rand_num = random.random()

            if rand_num < win_rate:
                profit = risk_per_trade * rrr
                print(i, 'win', profit)
            else:
                profit = risk_per_trade * -1
                print(i, 'lose', profit)

            profit_list.append({'simulation': simulation, 'index': i, 'profit': profit})

    print(profit_list)

    df = pd.DataFrame(profit_list)
    df['cumulative_profit'] = df.groupby('simulation')['profit'].cumsum()
    print(df)

    fig = px.line(df, x='index', y='cumulative_profit', color='simulation')

    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run()