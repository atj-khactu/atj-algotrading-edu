from dash import Dash, html, dcc, Input, Output, State, exceptions, dash_table
import dash_bootstrap_components as dbc
import MetaTrader5 as mt5
from datetime import datetime, timedelta, time
import pandas as pd
from PIL import Image
import plotly.express as px
import json

from atj_trading.backtester import Backtester, get_ohlc_history, create_price_fig

def create_app(json_file, num_candles=50, candle_step=1, strategy_name='Strategy'):
    with open(json_file) as jsonfile:
        data=json.loads(jsonfile.read())

    symbol = data['symbol']

    starting_balance = data['starting_balance']
    ohlc = pd.DataFrame(data['ohlc_history'])

    ohlc['time'] = pd.to_datetime(ohlc['time'])

    trades_df = pd.DataFrame(data['trade_history'])
    trades_df['open_time'] = pd.to_datetime(trades_df['open_time'])
    trades_df['close_time'] = pd.to_datetime(trades_df['close_time'])
    trades_df['commission'] = trades_df['commission'].round(2)
    trades_df['exchange_rate'] = data['exchange_rate']

    ohlc = ohlc[ohlc['time'] >= trades_df.iloc[0]['open_time']]

    def calc_profit(x):
        if x['order_type'] == 'buy':
            return round(((x['current_price'] - x['open_price']) * x['volume']) * x['exchange_rate'], 2)
        elif x['order_type'] == 'sell':
            return round(((x['open_price'] - x['current_price']) * x['volume']) * x['exchange_rate'], 2)

    app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
    app.layout = html.Div([
        dbc.Row([
            dbc.Col(html.H1('ATJ Traders - Backtester')),
            dbc.Col(html.H2(strategy_name, style={'text-align': 'right'})),
        ]),

        html.Div([
            dcc.Interval(id='interval', interval=500, n_intervals=0),
            html.Div(id='backtester-div'),

        ])

    ], style={'width': 1600, 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '20px'})


    @app.callback(
        Output('backtester-div', 'children'),
        Input('interval', 'n_intervals'),
    )
    def update_fig(n_intervals):
        print(n_intervals)

        n_intervals = n_intervals * candle_step

        initial_num_candles = num_candles
        if n_intervals > ohlc.shape[0] - initial_num_candles:
            raise exceptions.PreventUpdate

        new_ohlc = ohlc[n_intervals:initial_num_candles + n_intervals]

        new_fig = create_price_fig(new_ohlc, indicators=data['indicators'])
        new_fig.update_layout(title=data['symbol'], height=600, yaxis={'side': 'right'})

        time_min = new_ohlc.iloc[0]['time']
        time_max = new_ohlc.iloc[-1]['time']

        current_price = round(new_ohlc.iloc[-1]['close'], 5)

        open_trades = trades_df[(trades_df['open_time'].between(time_min, time_max)) & (trades_df['close_time'] > time_max)].copy()

        new_fig.add_hline(y=current_price, line_width=1, line_dash="solid", line_color="white")

        for i, d in open_trades.iterrows():
            new_fig.add_hline(y=d['open_price'], line_width=1, line_dash="dashdot", line_color="yellow")

            if d['sl'] != 0.0:
                new_fig.add_hline(y=d['sl'], line_width=1, line_dash="dashdot", line_color="red")
                new_fig.add_annotation(x=d['open_time'], y=d['sl'], text=ann_text, font=dict(size=17), showarrow=False, yshift=20)
            if d['tp'] != 0.0:
                new_fig.add_hline(y=d['tp'], line_width=1, line_dash="dashdot", line_color="red")
                new_fig.add_annotation(x=d['open_time'], y=d['tp'], text=ann_text, font=dict(size=17), showarrow=False, yshift=20)

            ann_text = f"{d['order_type']} {str(d['volume'])}"
            new_fig.add_annotation(x=d['open_time'], y=d['open_price'],
                                        text=ann_text,
                                        font=dict(size=17),
                                        showarrow=False,
                                        yshift=20)

            if d['order_type'] == 'buy':
                rect_color = 'green' if current_price >= d['open_price'] else 'red'
            elif d['order_type'] == 'sell':
                rect_color = 'red' if current_price >= d['open_price'] else 'green'

            new_fig.add_shape(type="rect",
                          x0=time_min, y0=d['open_price'], x1=time_max, y1=current_price,
                          line=dict(
                              color=rect_color,
                              width=1,
                          ),
                          fillcolor=rect_color,
                              opacity=0.2,
            )

        closed_trades = trades_df[trades_df['close_time'].between(time_min, time_max, inclusive='right')]

        for i, d in closed_trades.iterrows():
            line_color = 'green' if d['profit'] >= 0 else 'red'

            new_fig.add_shape(type="line",
                              x0=d['open_time'], y0=d['open_price'], x1=d['close_time'], y1=d['close_price'],
                              line=dict(
                                  color=line_color,
                                  width=2,
                                  dash="dashdot"))


        new_fig.update_xaxes(range=[time_min, time_max])

        # Open Trades

        open_trades['open_time'] = open_trades['open_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        open_trades['close_time'] = open_trades['close_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        open_trades['current_price'] = current_price
        open_trades['pnl'] = open_trades.apply(lambda x: calc_profit(x), axis=1)

        cols = ['symbol', 'open_time', 'open_price', 'order_type', 'volume', 'sl', 'tp', 'current_price', 'pnl']
        open_trades = open_trades[cols]

        open_trades_table = dash_table.DataTable(data=open_trades.to_dict('records'),
                                                 columns=[{"name": i, "id": i} for i in open_trades.columns],
                                                 style_cell={'backgroundColor': 'black', 'overflow': 'hidden',
                                                       'textOverflow': 'ellipsis',
                                                       'maxWidth': 0})

        # Pnl Chart
        closed_trades_total = trades_df[trades_df['close_time'] <= time_max].copy()

        closed_trades_total2 = closed_trades_total.copy()

        current_balance = round(closed_trades_total.iloc[-1]['balance'], 2)
        current_equity = round(current_balance + open_trades['pnl'].sum(), 2)

        closed_trades_total2.loc[0, ['close_time', 'balance']] = [ohlc['time'].min(), starting_balance]
        closed_trades_total2.loc[-1, ['close_time', 'balance']] = [time_max, current_equity]

        balance_fig = px.line(closed_trades_total2, x='close_time', y='balance', title='Pnl Chart', height=400, line_shape='hv')

        equity_color = 'green' if current_equity >= starting_balance else 'red'
        balance_fig.add_hline(y=current_equity, line_width=2, line_dash="solid", line_color=equity_color)
        balance_fig.add_hline(y=starting_balance, line_width=2, line_dash="solid", line_color='white', opacity=0.5)
        balance_fig.add_annotation(x=time_max, y=current_equity, text=f'Equity {current_equity}', font=dict(size=17), showarrow=False, yshift=20)

        # Closed Trades
        closed_trades_total = closed_trades_total.sort_values('close_time', ascending=False)

        closed_trades_total['open_time'] = closed_trades_total['open_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        closed_trades_total['close_time'] = closed_trades_total['close_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        cols = ['symbol', 'open_time', 'open_price', 'order_type', 'volume', 'close_time', 'close_price', 'sl', 'tp', 'commission', 'profit']
        closed_trades_total = closed_trades_total[cols]
        closed_trades_table = dash_table.DataTable(data=closed_trades_total.to_dict('records'),
                                                   columns=[{"name": i, "id": i} for i in closed_trades_total.columns],
                                                   style_cell={'backgroundColor': 'black', 'overflow': 'hidden',
                                                       'textOverflow': 'ellipsis',
                                                       'maxWidth': 0},
                                                   )

        # General Statistics
        floating_pnl = current_equity - current_balance
        total_pnl = floating_pnl + closed_trades_total['profit'].sum() + closed_trades_total['commission'].sum()
        total_pnl = round(total_pnl, 2)

        num_trades = closed_trades_total.shape[0] + open_trades.shape[0]
        num_wins = closed_trades_total[closed_trades_total['profit'] > 0].shape[0]
        # num_losses = closed_trades_total[closed_trades_total['profit'] < 0].shape[0]
        win_rate = round((num_wins / num_trades) * 100, 2)

        stats = html.Div([
            dbc.Row([
                dbc.Col(html.Div([
                    html.H4('PnL:', style={'text-align': 'center', 'color': '#D3D3D3'}),
                    html.H3(str(total_pnl), style={'color': equity_color, 'text-align': 'center'})
                ])),
                dbc.Col(html.Div([
                    html.H4('Num Trades:', style={'text-align': 'center', 'color': '#D3D3D3'}),
                    html.H3(str(num_trades), style={'text-align': 'center'})
                    ])),
                dbc.Col(html.Div([
                    html.H4('Win Rate:', style={'text-align': 'center', 'color': '#D3D3D3'}),
                    html.H3(str(win_rate) + '%', style={'text-align': 'center'})
                ]))

            ]),
            ], style={'padding-top': '30px'})

        strategy_info = html.Div([
            stats
        ], style={'background-color': '#111111', 'box-sizing': 'border-box', 'padding': '20px', 'margin-top': '20px', 'height': '180px'})

        row1 = dbc.Row(
                    [
                        dbc.Col(html.Div([dcc.Graph(figure=new_fig)])),
                        dbc.Col(html.Div([dcc.Graph(figure=balance_fig),
                                          strategy_info
                                        ])
                                )
                    ]
                )

        return [
            row1,

            html.Hr(),

            html.Div([
                html.H2('Open Trades'),
                open_trades_table
            ], style={'background-color': '#111111', 'box-sizing': 'border-box', 'padding': '20px'}),

            html.Hr(),

            html.Div([
                html.H2('Closed Trades'),
                closed_trades_table
            ], style={'background-color': '#111111', 'box-sizing': 'border-box', 'padding': '20px'})

            ]

    return app

if __name__ == '__main__':
    app = create_app('bollinger_backtest.json')
    app.run()
