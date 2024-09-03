from dash import Dash, html, dcc, Output, Input, State, dash_table, exceptions, ctx
import dash_bootstrap_components as dbc
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.io as pio

from atj_trading.backtester import create_price_fig, get_ohlc_history
from atj_trading.mt5_trade_utils import get_positions

from config import mt5_credentials

pio.templates.default = "plotly_dark"
pd.set_option('display.width', None)

mt5.initialize(mt5_credentials['exe_path'])
# mt5.login(mt5_credentials['login'], mt5_credentials['password'], mt5_credentials['server'])

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div([
    dcc.Interval(id='interval', interval=5000, n_intervals=0),
    dcc.Store(id='store-selected-trade'),
    html.H1('Account Dashboard'),
    html.Hr(),

    html.Div(id='store-output'),
    html.Div(id='page-content')

], style={'margin-left': '5%', 'margin-right': '5%', 'margin-top': '20px'})


@app.callback(Output('page-content', 'children'),
              Input('interval', 'n_intervals'),
              Input('store-selected-trade', 'data'),)
def update_page(n_intervals, selected_trade):
    type_dict = {0: 'buy', 1: 'sell', 2: 'deposit'}

    open_selected_rows = []
    closed_selected_rows = []
    if selected_trade:
        if selected_trade['type_row'] == 'opened':
            open_selected_rows = [selected_trade['row_id']]
        elif selected_trade['type_row'] == 'closed':
            closed_selected_rows = [selected_trade['row_id']]


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
    trades_df['order_type'] = trades_df['order_type'].apply(lambda x: type_dict[x])
    trades_df = trades_df.sort_values('open_time', ascending=False)

    out_deals = deals_df[deals_df['entry'] == 1].copy()

    out_deals['pnl'] = out_deals['profit'].cumsum()
    out_deals_by_date = out_deals.groupby('date', as_index=False)['pnl'].last()

    pnl_fig = px.line(out_deals_by_date, x='date', y='pnl', title='PnL', height=500)

    trades_table = dash_table.DataTable(
        id='closed-trades-table',
        data=trades_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in trades_df.columns],
        style_cell={'background-color': '#111111'},
        page_size=20,
        row_selectable='single',
        cell_selectable=False,
        selected_rows=closed_selected_rows
    )

    open_trades_df = get_positions()
    open_trades_df['time'] = pd.to_datetime(open_trades_df['time'], unit='s')
    open_trades_df['type'] = open_trades_df['type'].apply(lambda x: type_dict[x])
    open_trades_df = open_trades_df.sort_values('time', ascending=False)

    open_trades_table = dash_table.DataTable(
        id='open-trades-table',
        data=open_trades_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in open_trades_df.columns],
        style_cell={'background-color': '#111111'},
        page_size=20,
        row_selectable='single',
        cell_selectable=False,
        selected_rows=open_selected_rows
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

    trade_fig = create_trade_chart(selected_trade)

    return [
        html.Div([stats_row], style={'height': '100px', 'width': '100%', 'background-color': '#111111'}),
        html.Br(),

        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=pnl_fig),
            ]),
            dbc.Col([
                dcc.Graph(figure=trade_fig)
            ])
        ]),

        html.Br(),

        html.H2('Open Trades'),
        open_trades_table,

        html.Br(),

        html.H2('Closed Trades'),
        trades_table
    ]

@app.callback(
    Output('store-selected-trade', 'data'),
    Input('open-trades-table', 'selected_rows'),
    State('open-trades-table', 'data'),
    Input('closed-trades-table', 'selected_rows'),
    State('closed-trades-table', 'data')
)
def save_open_trade_data(open_trade_row, open_data, closed_trade_row, closed_data):

    if len(ctx.triggered) == 2:
        raise exceptions.PreventUpdate

    if ctx.triggered[0]['prop_id'] == 'open-trades-table.selected_rows':
        open_trade = open_data[open_trade_row[0]]
        open_trade['type_row'] = 'opened'
        open_trade['row_id'] = open_trade_row[0]
        return open_trade
    elif ctx.triggered[0]['prop_id'] == 'closed-trades-table.selected_rows':
        closed_trade = closed_data[closed_trade_row[0]]
        closed_trade['type_row'] = 'closed'
        closed_trade['row_id'] = closed_trade_row[0]
        return closed_trade


@app.callback(
    Output('store-output', 'children'),
    Input('store-selected-trade', 'data')
)
def show_store_output(data):
    return [str(data)]


def create_trade_chart(trade_data):

    if not trade_data:
        return px.line(height=500, title='Trade Chart')

    if trade_data['type_row'] == 'opened':
        ticket = trade_data['ticket']
        symbol = trade_data['symbol']
        volume = trade_data['volume']
        order_type = trade_data['type']
        open_time = trade_data['time']
        open_price = trade_data['price_open']
        close_time = datetime.now()
        close_price = trade_data['price_current']
        sl = trade_data['sl']
        tp = trade_data['tp']

        open_time = pd.to_datetime(open_time)
        close_time = pd.to_datetime(close_time)

        start_dt = open_time - timedelta(hours=3)
        end_dt = close_time + timedelta(hours=3)

        ohlc = get_ohlc_history(symbol, mt5.TIMEFRAME_M15, start_dt, end_dt)

        trades_fig = create_price_fig(ohlc, title=f"{symbol} - {str(ticket)}", height=500)

        trades_fig.add_hline(y=close_price, line_width=1, line_dash="solid", line_color="white")

        trades_fig.add_hline(y=open_price, line_width=1, line_dash="dashdot", line_color="yellow")

        if sl != 0.0:
            trades_fig.add_hline(y=sl, line_width=1, line_dash="dashdot", line_color="red")
            trades_fig.add_annotation(x=open_time, y=sl, text='sl', font=dict(size=17),
                                      showarrow=False, yshift=20)
        if tp != 0.0:
            trades_fig.add_hline(y=tp, line_width=1, line_dash="dashdot", line_color="red")
            trades_fig.add_annotation(x=open_time, y=tp, text='tp', font=dict(size=17),
                                      showarrow=False, yshift=20)

        ann_text = f"{order_type} {str(volume)}"
        trades_fig.add_annotation(x=open_time, y=open_price,
                                  text=ann_text,
                                  font=dict(size=17),
                                  showarrow=False,
                                  yshift=20)

        if order_type == 'buy':
            rect_color = 'green' if close_price >= open_price else 'red'
        elif order_type == 'sell':
            rect_color = 'red' if close_price >= open_price else 'green'

        trades_fig.add_shape(type="rect",
                             x0=start_dt, y0=open_price, x1=end_dt, y1=close_price,
                             line=dict(
                                 color=rect_color,
                                 width=1,
                             ),
                             fillcolor=rect_color,
                             opacity=0.2,
                             )

        trades_fig.add_vline(x=open_time, line_color='white', line_width=1, line_dash='dash', opacity=0.4)

    elif trade_data['type_row'] == 'closed':
        ticket = trade_data['position_id']
        symbol = trade_data['symbol']
        volume = trade_data['volume']
        order_type = trade_data['order_type']
        open_time = trade_data['open_time']
        open_price = trade_data['open_price']
        close_time = trade_data['close_time']
        close_price = trade_data['close_price']
        profit = trade_data['profit']
        sl = 0.0
        tp = 0.0

        open_time = pd.to_datetime(open_time)
        close_time = pd.to_datetime(close_time)

        line_color = 'green' if profit >= 0 else 'red'

        start_dt = open_time - timedelta(hours=3)
        end_dt = close_time + timedelta(hours=3)
        ohlc = get_ohlc_history(symbol, mt5.TIMEFRAME_M15, start_dt, end_dt)
        trades_fig = create_price_fig(ohlc, title=f"{symbol} - {str(ticket)}", height=500)

        trades_fig.add_shape(type="line",
                          x0=open_time, y0=open_price, x1=close_time, y1=close_price,
                          line=dict(
                              color=line_color,
                              width=2,
                              dash="dashdot"))

    return trades_fig


if __name__ == '__main__':
    app.run(port=8050)