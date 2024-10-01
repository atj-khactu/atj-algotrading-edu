from dash import Dash, html, Output, Input, State, dash_table, dcc
import dash_bootstrap_components as dbc
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from projects.atj_trading_legacy.backtester import get_ohlc_history
import plotly.express as px

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div([
    html.H1('Market Analysis App'),
    html.Hr(),

    dbc.Label('Symbol: ', style={'display': 'inline-block'}),
    dbc.Input(id='symbol-input', style={'width': '250px', 'display': 'inline-block', 'margin-left': '20px'}),
    dbc.Button('Submit', id='submit-btn', style={'margin-top': '-3px'}),

    html.Div(id='symbol-analysis-div')

], style={'margin-left': '5%', 'margin-right': '5%', 'margin-top': '20px'})


def analyze_symbol(symbol):
    symbol = symbol
    timeframe = mt5.TIMEFRAME_D1
    start_dt = datetime.now() - timedelta(days=365 * 10)
    end_dt = datetime.now()

    ohlc_df = get_ohlc_history(symbol, timeframe, start_dt, end_dt)

    ohlc_df['gain'] = ohlc_df['open'].shift(-1) - ohlc_df['open']
    ohlc_df['perc_gain'] = (ohlc_df['gain'] / ohlc_df['open']) * 100

    ohlc_df['month'] = ohlc_df['time'].dt.month
    ohlc_df['year'] = ohlc_df['time'].dt.year

    gain_by_month = ohlc_df.groupby(['year', 'month'], as_index=False)['perc_gain'].sum()
    fig = px.bar(gain_by_month, x='month', y='perc_gain', title='Gain by month', color='year')

    return gain_by_month, fig


@app.callback(Output('symbol-analysis-div', 'children'),
              Input('submit-btn', 'n_clicks'),
              State('symbol-input', 'value'))
def serve_analysis_page(n_clicks, symbol):
    print(n_clicks, symbol)

    if n_clicks and symbol:
        gain_by_month_df, fig = analyze_symbol(symbol)

        table = dash_table.DataTable(data=gain_by_month_df.to_dict('records'),
                                     columns=[{"name": i, "id": i} for i in gain_by_month_df.columns],
                                     style_cell={'backgroundColor': 'black'})
        return [
            dcc.Graph(figure=fig),
            table
        ]


if __name__ == '__main__':
    connected = mt5.initialize()
    print('Connected to MT5:', connected)

    app.run()
