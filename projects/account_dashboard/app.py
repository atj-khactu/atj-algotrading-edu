from dash import Dash, html, dcc, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.io as pio

from config import mt5_credentials

pio.templates.default = "plotly_dark"
pd.set_option('display.width', None)

mt5.initialize(mt5_credentials['exe_path'])
mt5.login(mt5_credentials['login'], mt5_credentials['password'], mt5_credentials['server'])

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div([
    dcc.Interval(id='interval', interval=5000, n_intervals=0),
    html.H1('Account Dashboard'),
    html.Hr(),

    html.Div(id='page-content')

], style={'margin-left': '5%', 'margin-right': '5%', 'margin-top': '20px'})


@app.callback(Output('page-content', 'children'),
              Input('interval', 'n_intervals'))
def update_page(n_intervals):

    deals = mt5.history_deals_get(datetime(2000, 1, 1), datetime.now() + timedelta(hours=3))
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

    out_deals = deals_df[deals_df['entry'] == 1].copy()

    out_deals['pnl'] = out_deals['profit'].cumsum()
    out_deals_by_date = out_deals.groupby('date', as_index=False)['pnl'].last()

    pnl_fig = px.line(out_deals_by_date, x='date', y='pnl', title='PnL')

    trades_table = dash_table.DataTable(
        data=trades_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in trades_df.columns],
        style_cell={'background-color': '#111111'},
        page_size=20
    )

    open_trades_df = get_positions()
    open_trades_table = dash_table.DataTable(
        data=open_trades_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in open_trades_df.columns],
        style_cell={'background-color': '#111111'},
        page_size=20
    )

    account_info = mt5.account_info()

    balance = account_info.balance
    equity = account_info.equity
    floating_pnl = round(equity - balance, 2)
    ytd_profit = round(equity - deals_df[deals_df['type'] == 2]['profit'].sum(), 2)

    floating_pnl_color = 'green' if floating_pnl >= 0 else 'red'
    ytd_profit_color = 'green' if ytd_profit >= 0 else 'red'

    stats_row = dbc.Row([
        dbc.Col(html.Div([html.H4('Floating PnL'), html.H3(floating_pnl, style={'color': floating_pnl_color})]),
                style={'text-align': 'center'}),
        dbc.Col(html.Div([html.H4('Balance'), html.H3(balance)]), style={'text-align': 'center'}),
        dbc.Col(html.Div([html.H4('Equity'), html.H3(equity)]), style={'text-align': 'center'}),
        dbc.Col(html.Div([html.H4('YTD Profit'), html.H3(ytd_profit, style={'color': ytd_profit_color})]),
                style={'text-align': 'center'}),
    ], style={'margin-left': '5%', 'margin-right': '5%', 'padding-top': '10px'})

    return [
        html.Div([stats_row], style={'height': '100px', 'width': '100%', 'background-color': '#111111'}),
        html.Br(),

        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=pnl_fig),

            ]),
            dbc.Col('Trade Replay'),

        ]),

        html.Br(),

        html.H2('Open Trades'),
        open_trades_table,

        html.Br(),

        html.H2('Historical Trades'),
        trades_table
    ]


def get_positions(magic=None):
    if mt5.positions_total():
        positions = mt5.positions_get()
        positions_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())

        if magic:
            positions_df = positions_df[positions_df['magic'] == magic]

        return positions_df

    else:
        return pd.DataFrame(columns=['ticket', 'time', 'time_msc', 'time_update', 'time_update_msc', 'type',
                                     'magic', 'identifier', 'reason', 'volume', 'price_open', 'sl', 'tp',
                                     'price_current', 'swap', 'profit', 'symbol', 'comment', 'external_id'])


if __name__ == '__main__':
    app.run()