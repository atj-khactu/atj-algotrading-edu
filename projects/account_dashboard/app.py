from dash import Dash, html, dcc, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
import MetaTrader5 as mt5
from config import initialize_mt5
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_dark"
initialize_mt5()

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

    out_deals = deals_df[deals_df['entry'] == 1].copy()
    out_deals['pnl'] = out_deals['profit'].cumsum()
    out_deals_by_date = out_deals.groupby('date', as_index=False)['pnl'].last()

    pnl_fig = px.line(out_deals_by_date, x='date', y='pnl', title='PnL')

    table = dash_table.DataTable(
        data=deals_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in deals_df.columns],
        style_cell={'background-color': 'black'},
        page_size=20
    )

    return [
        dcc.Graph(figure=pnl_fig),
        table
    ]


if __name__ == '__main__':
    app.run()