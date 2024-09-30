from dash import Dash, html, dcc, Output, Input
import MetaTrader5 as mt5
from datetime import datetime
from projects.atj_trading_legacy.backtester import get_ohlc_history, create_price_fig
from config import mt5_credentials

mt5.initialize()
mt5.login(mt5_credentials['login'], mt5_credentials['password'], mt5_credentials['server'])

symbol = 'EURUSD'
timeframe = mt5.TIMEFRAME_D1

start_dt = datetime(2023, 1 ,1)
end_dt = datetime.now()

ohlc = get_ohlc_history(symbol, timeframe, start_dt, end_dt)
print(ohlc)


app = Dash(__name__)

app.layout = html.Div([
    dcc.Interval(id='interval', interval=1000, n_intervals=0),

    html.H1('Support and Resistance Visualization'),

    dcc.Graph(id='price-figure')
])


@app.callback(Output('price-figure', 'figure'),
              Input('interval', 'n_intervals'))
def update_figure(n_intervals):

    new_ohlc = ohlc[n_intervals:50+n_intervals]

    resistance = new_ohlc[-11:-1]['high'].max()
    support = new_ohlc[-11:-1]['low'].min()

    price_figure = create_price_fig(new_ohlc)
    price_figure.update_layout(height=800)

    price_figure.add_shape(type="line",
                      x0=new_ohlc.iloc[-11]['time'], y0=support, x1=new_ohlc.iloc[-1]['time'], y1=support,
                      line=dict(
                          color="yellow",
                          width=4,
                          dash="dashdot"))

    price_figure.add_shape(type="line",
                           x0=new_ohlc.iloc[-11]['time'], y0=resistance, x1=new_ohlc.iloc[-1]['time'], y1=resistance,
                           line=dict(
                               color="yellow",
                               width=4,
                               dash="dashdot"))

    price_figure.add_annotation(x=new_ohlc.iloc[-11]['time'], y=resistance,
                           text="Resistance",
                           font=dict(size=17),
                           showarrow=False,
                           yshift=20)

    price_figure.add_annotation(x=new_ohlc.iloc[-11]['time'], y=support,
                                text="Support",
                                font=dict(size=17),
                                showarrow=False,
                                yshift=-20)

    if new_ohlc.iloc[-1]['close'] > resistance:
        price_figure.add_annotation(x=new_ohlc.iloc[-1]['time'], y=resistance,
                               text="Breakout!",
                               font=dict(size=17),
                               showarrow=False,
                               yshift=20)
    elif new_ohlc.iloc[-1]['close'] < support:
        price_figure.add_annotation(x=new_ohlc.iloc[-1]['time'], y=support,
                               text="Breakout!",
                               font=dict(size=17),
                               showarrow=False,
                               yshift=-20)

    print(n_intervals)

    return price_figure


if __name__ == '__main__':
    app.run(port=8000)