import MetaTrader5 as mt5
from datetime import datetime, timedelta
from atj_algotrading.backtester import get_ohlc_history, create_price_fig
from time import sleep
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go

mt5.initialize()

symbol = 'USTEC'
start_dt = datetime.now() - timedelta(days=365)
end_dt = datetime.now()

ohlc = get_ohlc_history(symbol, mt5.TIMEFRAME_H1, start_dt, end_dt)
ohlc['date'] = ohlc['time'].dt.date


app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.layout = html.Div([
    dcc.Interval(id='interval', interval=500),
    html.H1('Price Action Backtester'),
    html.Hr(),

    html.Div(id='price-chart')
], style={'width': 1600, 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '20px'})

@app.callback(Output('price-chart', 'children'),
              [Input('interval', 'n_intervals')])
def update_ohlc_chart(n_intervals):
    num_candles = 100
    new_ohlc_data = ohlc[n_intervals:n_intervals+num_candles]

    min_max_df =get_hls(new_ohlc_data)
    print(min_max_df)

    fig = create_price_fig(new_ohlc_data)
    fig.add_trace(go.Scatter(x=min_max_df['time'], y=min_max_df['value'], mode="lines"))

    return dcc.Graph(figure=fig)


def get_hls(ohlc):
    ohlc_max_values = ohlc.sort_values(['date', 'high'], ascending=[True, False])[['time', 'date', 'high']]
    ohlc_max_values2 = ohlc_max_values.groupby('date').first()
    ohlc_max_values2['type'] = 'high'
    ohlc_max_values2 = ohlc_max_values2.rename(columns={'high': 'value'})

    ohlc_min_values = ohlc.sort_values(['date', 'low'], ascending=[True, True])[['time', 'date', 'low']]
    ohlc_min_values2 = ohlc_min_values.groupby('date').first()
    ohlc_min_values2['type'] = 'low'
    ohlc_min_values2 = ohlc_min_values2.rename(columns={'low': 'value'})

    min_max_df = pd.concat([ohlc_max_values2, ohlc_min_values2])
    min_max_df = min_max_df.sort_values('time')

    min_max_df['prev_type'] = min_max_df['type'].shift(1)
    min_max_df['prev_value'] = min_max_df['value'].shift(1)
    min_max_df['prev_time'] = min_max_df['time'].shift(1)
    min_max_df['same_type_in_a_row'] = min_max_df.apply(lambda x: 1 if x['type'] == x['prev_type'] else 0, axis=1)

    def choose_min_max_value(x):
        if x['same_type_in_a_row'] == 1 and x['type'] == 'low':
            if x['value'] < x['prev_value']:
                return x['value'], x['time']
            else:
                return x['prev_value'], x['prev_time']

        elif x['same_type_in_a_row'] == 1 and x['type'] == 'high':
            if x['value'] > x['prev_value']:
                return x['value'], x['time']
            else:
                return x['prev_value'], x['prev_time']

    min_max_df['new_data'] = min_max_df.apply(choose_min_max_value, axis=1)
    min_max_df['new_data'] = min_max_df['new_data'].shift(-1)

    def overwrite_value(x):
        if x['new_data']:
            return x['new_data'][0]
        else:
            return x['value']

    def overwrite_time(x):
        if x['new_data']:
            return x['new_data'][1]
        else:
            return x['time']

    min_max_df['time'] = min_max_df.apply(overwrite_time, axis=1)
    min_max_df['value'] = min_max_df.apply(overwrite_value, axis=1)

    min_max_df = min_max_df[min_max_df['same_type_in_a_row'] == 0]

    return min_max_df[['time', 'value', 'type']]


if __name__ == '__main__':
    app.run(port=8088)
