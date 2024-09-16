from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas as pd


def get_historical_trades(start_dt, end_dt):
    type_dict = {0: 'buy', 1: 'sell', 2: 'deposit'}

    deals = mt5.history_deals_get(start_dt, end_dt)
    deals_df = pd.DataFrame(deals, columns=deals[0]._asdict().keys())
    deals_df['time'] = pd.to_datetime(deals_df['time'], unit='s')
    deals_df['date'] = deals_df['time'].dt.date

    in_cols = ['position_id', 'time', 'symbol', 'type', 'commission', 'price', 'magic']
    deals_df_in = deals_df[deals_df['entry'] == 0][in_cols]

    out_cols = ['position_id', 'time', 'volume', 'price', 'commission', 'swap', 'profit', 'comment']
    deals_df_out = deals_df[deals_df['entry'] == 1][out_cols]

    trades_df = deals_df_in.merge(deals_df_out, on='position_id', suffixes=['_in', '_out'])
    trades_df = trades_df.rename(columns={'time_in': 'open_time', 'time_out': 'close_time',
                                          'price_in': 'open_price', 'price_out': 'close_price',
                                          'type': 'order_type'})

    trades_df['commission'] = trades_df['commission_in'] + trades_df['commission_out']

    trades_df = trades_df[['position_id', 'symbol', 'open_time', 'open_price', 'order_type', 'volume',
                           'close_time', 'close_price', 'swap', 'commission', 'profit']]
    trades_df['order_type'] = trades_df['order_type'].apply(lambda x: type_dict[x])
    trades_df = trades_df.sort_values('open_time', ascending=False)

    return trades_df


app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.layout = html.Div([
    dcc.Interval(id='interval', interval=1000),
    html.Div(id='stats-div')

], style={'background-color': 'transparent', 'text-align': 'center'})


@app.callback(Output('stats-div', 'children'),
              Input('interval', 'n_intervals'))
def update_outputs(n_intervals):

    start_dt = datetime.now().replace(day=1)
    end_dt = datetime.now() + timedelta(hours=3)

    mt5.initialize()
    trades = get_historical_trades(start_dt, end_dt)

    print(trades)

    mtd_profit = round(trades['profit'].sum(), 2)
    print('MTD Profit', mtd_profit)

    account_info = mt5.account_info()
    floating_pnl = round(account_info.equity - account_info.balance, 2)
    print('Floating PnL', floating_pnl)

    num_profits = trades[trades['profit'] > 0].shape[0]
    num_losses = trades[trades['profit'] < 0].shape[0]

    print('Num Profits', num_profits)
    print('Num Losses', num_losses)

    return dbc.Row([
            dbc.Col(html.Div([
                html.H4('MTD Profit'),
                html.H3(str(mtd_profit) + ' EUR')
            ])),

            dbc.Col(html.Div([
                html.H4('Floating PnL'),
                html.H3(str(floating_pnl) + ' EUR')
            ])),

            dbc.Col(html.Div([
                html.H4('Num Profits'),
                html.H3(num_profits)
            ])),

            dbc.Col(html.Div([
                html.H4('Num Losses'),
                html.H3(num_losses)
            ])),
    ])


if __name__ == '__main__':

    app.run(port=8051)
