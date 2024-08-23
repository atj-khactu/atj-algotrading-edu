from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc

import MetaTrader5 as mt5
from IPython.display import display
from datetime import datetime
import plotly.express as px

from atj_trading.backtester import get_ohlc_history, create_price_fig
from config import mt5_credentials

mt5.initialize()
mt5.login(mt5_credentials['login'], mt5_credentials['password'], mt5_credentials['server'])

symbol = 'EURUSD'
timeframe = mt5.TIMEFRAME_D1
period = 20

start_dt = datetime(2023, 1, 1)
end_dt = datetime.now()

ohlc = get_ohlc_history(symbol, timeframe, start_dt, end_dt)
display(ohlc)

price_fig = create_price_fig(ohlc)

ohlc['support'] = ohlc['low'].shift(1).rolling(period).min()
ohlc['resistance'] = ohlc['high'].shift(1).rolling(period).max()

app = Dash(__name__)
app.layout = html.Div([

    html.Div([
        dcc.Interval(id='interval', interval=1000, n_intervals=0),
        html.H1('Support & Resistance Visualisation'),
        dcc.Graph(id='ohlc_fig')
    ])

], style={'margin-left:': '20px', 'margin-right': '20px', 'margin-top': '10px'})


@app.callback(
    Output('ohlc_fig', 'figure'),
    Input('interval', 'n_intervals')
)
def update_fig(n_intervals):
    print(n_intervals)

    new_ohlc = ohlc[n_intervals:100 + n_intervals]

    support = new_ohlc[-21:-1]['close'].min()
    resistance = new_ohlc[-21:-1]['close'].max()

    new_fig = create_price_fig(new_ohlc)
    new_fig.update_layout(height=800)

    new_fig.add_shape(type="line",
                      x0=new_ohlc.iloc[-21]['time'], y0=support, x1=new_ohlc.iloc[-1]['time'], y1=support,
                      line=dict(
                          color="yellow",
                          width=4,
                          dash="dashdot"))

    new_fig.add_shape(type="line",
                      x0=new_ohlc.iloc[-21]['time'], y0=resistance, x1=new_ohlc.iloc[-1]['time'], y1=resistance,
                      line=dict(
                          color="yellow",
                          width=4,
                          dash="dashdot"))

    new_fig.add_annotation(x=new_ohlc.iloc[-21]['time'], y=resistance,
                           text="Resistance",
                           font=dict(size=17),
                           showarrow=False,
                           yshift=20)

    new_fig.add_annotation(x=new_ohlc.iloc[-21]['time'], y=support,
                           text="Support",
                           font=dict(size=17),
                           showarrow=False,
                           yshift=-20)

    if new_ohlc.iloc[-1]['close'] > resistance:
        new_fig.add_annotation(x=new_ohlc.iloc[-1]['time'], y=resistance,
                               text="Breakout!",
                               font=dict(size=17),
                               showarrow=False,
                               yshift=20)
    elif new_ohlc.iloc[-1]['close'] < support:
        new_fig.add_annotation(x=new_ohlc.iloc[-1]['time'], y=support,
                               text="Breakout!",
                               font=dict(size=17),
                               showarrow=False,
                               yshift=-20)

    return new_fig


if __name__ == '__main__':
    app.run()
