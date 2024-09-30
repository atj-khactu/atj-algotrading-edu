"""This is ATJ Traders' Backtester. For more information visit: https://www.youtube.com/@ATJTraders618"""

import pandas as pd
import MetaTrader5 as mt5
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
from IPython.display import display

pio.templates.default = "plotly_dark"


class _Orders():
    def __init__(self):
        self.orders = []

    def open_trade(self, symbol, volume, order_type, sl=0, tp=0, info={}):
        order = {
            'action': 'entry',
            'symbol': symbol,
            'volume': volume,
            'order_type': order_type,
            'sl': sl,
            'tp': tp,
            'info': info
        }

        self.orders.append(order)

    def close_trade(self, trade):
        trade_id = trade.name
        order = {
            'action': 'exit',
            'trade_id': trade_id,
        }

        self.orders.append(order)

    def modify_sl(self, trade, sl):
        trade_id = trade.name
        order = {
            'action': 'modify_sl',
            'trade_id': trade_id,
            'sl': sl
        }

        self.orders.append(order)

    def modify_tp(self, trade, tp):
        trade_id = trade.name
        order = {
            'action': 'modify_tp',
            'trade_id': trade_id,
            'tp': tp
        }

        self.orders.append(order)

class Backtester():
    def __init__(self):
        self.exchange_rate = 1
        self.commission = 0
        self.swap_long = 0
        self.swap_short = 0
        self.triple_swap_day = 4

        self.ohlc_data = None
        self.on_bar = None

        self.trades = pd.DataFrame(
            columns=['state', 'symbol', 'order_type', 'volume', 'open_time', 'open_price', 'close_time',
                     'close_price', 'sl', 'tp', 'info'])

    def set_starting_balance(self, starting_balance, currency='EUR'):
        self.starting_balance = starting_balance
        self.currency = currency

    def set_exchange_rate(self, exchange_rate):
        self.exchange_rate = exchange_rate

    def set_commission(self, commission):
        self.commission = commission

    def set_swaps(self, swap_long, swap_short, triple_swap_day):
        self.swap_long = swap_long
        self.swap_short = swap_short
        self.triple_swap_day = triple_swap_day

    def set_historical_data(self, ohlc_data):
        self.ohlc_data = ohlc_data

    def set_on_bar(self, on_bar):
        self.on_bar = on_bar


    def run_backtest(self):

        # commission must be negative
        if self.commission >= 0:
            self.commission = self.commission * -1

        for i in self.ohlc_data.index:
            data = self.ohlc_data.loc[i]

            self.orders = _Orders()

            # Generating Orders
            self.on_bar(data, self.trades, self.orders)

            for order in self.orders.orders:

                if order['action'] == 'entry':
                    self.trades.loc[len(self.trades), self.trades.columns] = ['open', order['symbol'],
                                                                              order['order_type'], order['volume'],
                                                                              data['time'], data['open'], '', '',
                                                                              order['sl'], order['tp'], order['info']]
                elif order['action'] == 'exit':
                    self.trades.loc[order['trade_id'], ['state', 'close_time', 'close_price']] = ['closed',
                                                                                                   data['time'],
                                                                                                   data['open']]
                elif order['action'] == 'modify_sl':
                    self.trades.loc[order['trade_id'], ['sl']] = [order['sl']]

                elif order['action'] == 'modify_tp':
                    self.trades.loc[order['trade_id'], ['tp']] = [order['tp']]

            open_trades = self.trades[self.trades['state'] == 'open']
            # close positions that hit sl or tp, iterating though open trades with index x
            for x in open_trades.index:
                t = open_trades.loc[x]
                if t['order_type'] == 'buy':
                    if t['sl'] >= data['low'] and t['sl'] != 0:
                        # filling exactly at SL price might cause inaccuracy in backtest as you will receive slippage
                        # many times.
                        self.trades.loc[x, ['state', 'close_time', 'close_price']] = ['closed', data['time'],
                                                                                      t['sl']]
                    elif t['tp'] <= data['high'] and t['tp'] != 0:
                        self.trades.loc[x, ['state', 'close_time', 'close_price']] = ['closed', data['time'],
                                                                                      t['tp']]

                elif t['order_type'] == 'sell':
                    if t['sl'] <= data['high'] and t['sl'] != 0:
                        # filling exactly at SL price might cause inaccuracy in backtest as you will receive slippage
                        # many times.
                        self.trades.loc[x, ['state', 'close_time', 'close_price']] = ['closed', data['time'],
                                                                                      t['sl']]
                    elif t['tp'] >= data['low'] and t['tp'] != 0:
                        self.trades.loc[x, ['state', 'close_time', 'close_price']] = ['closed', data['time'],
                                                                                      t['tp']]

        # used for closing trades at the end of backtest
        last_time = self.ohlc_data.iloc[-1]['time']
        last_close = self.ohlc_data.iloc[-1]['close']

        # after backtest is over, close all open positions
        self.trades.loc[self.trades['state'] == 'open', ['state', 'close_time', 'close_price']] = ['closed', last_time,
                                                                                                   last_close]

        # evaluate backtest profits
        def calc_profit(x):
            if x['order_type'] == 'buy':
                return ((x['close_price'] - x['open_price']) * x['volume']) * self.exchange_rate
            elif x['order_type'] == 'sell':
                return ((x['open_price'] - x['close_price']) * x['volume']) * self.exchange_rate

        self.trades['profit'] = self.trades.apply(calc_profit, axis=1).round(2)
        self.trades['commission'] = self.commission * self.trades['volume']
        self.trades['profit_net'] = self.trades['profit'] + self.trades['commission']
        self.trades['profit_cumulative'] = self.trades['profit_net'].cumsum()
        self.trades['balance'] = self.trades['profit_cumulative'] + self.starting_balance

        return self.trades

    def visualize_backtest(self, indicators=[], num_trades=None):
        # visualize backtest

        if indicators:
            fig = px.line(self.ohlc_data, x='time', y=indicators, height=600, title='Backtest Trades')
            fig.add_trace(go.Candlestick(x=self.ohlc_data['time'],
                                         open=self.ohlc_data['open'],
                                         high=self.ohlc_data['high'],
                                         low=self.ohlc_data['low'],
                                         close=self.ohlc_data['close'], name='OHLC Data'))
            fig.update_layout(xaxis_rangeslider_visible=False)
        else:
            fig = go.Figure(data=[go.Candlestick(x=self.ohlc_data['time'],
                                                 open=self.ohlc_data['open'],
                                                 high=self.ohlc_data['high'],
                                                 low=self.ohlc_data['low'],
                                                 close=self.ohlc_data['close'], name='OHLC Data')])

            fig.update_layout(height=600, title='Backtest Trades')
            fig.update_layout(xaxis_rangeslider_visible=False)

        if num_trades:
            for i, trade in self.trades.tail(num_trades).iterrows():
                color = 'green' if trade['profit'] > 0 else 'red'
                fig.add_shape(type="line",
                              x0=trade['open_time'], y0=trade['open_price'], x1=trade['close_time'],
                              y1=trade['close_price'],
                              line=dict(
                                  color=color,
                                  width=5,
                              )
                              )
        else:
            for i, trade in self.trades.iterrows():
                color = 'green' if trade['profit'] > 0 else 'red'
                fig.add_shape(type="line",
                              x0=trade['open_time'], y0=trade['open_price'], x1=trade['close_time'],
                              y1=trade['close_price'],
                              line=dict(
                                  color=color,
                                  width=5,
                              )
                              )

        return fig

    def plot_pnl(self):
        fig = px.line(self.trades, x='open_time', y='profit_cumulative', title='PnL Graph')
        return fig

    def plot_balance(self):
        fig = px.line(self.trades, x='close_time', y='balance', title='Balance Graph')
        return fig

    def export_to_json(self, filename, symbol='', indicators=[]):
        import json

        ohlc_data = self.ohlc_data.copy()

        for col in ohlc_data.columns:
            if col in ['time', 'date']:
                ohlc_data[col] = ohlc_data[col].astype(str)

        trades = self.trades.copy()
        trades['open_time'] = trades['open_time'].astype(str)
        trades['close_time'] = trades['close_time'].astype(str)

        data = {
            'symbol': symbol,
            'indicators': indicators,
            'starting_balance': self.starting_balance,
            'exchange_rate': self.exchange_rate,
            'ohlc_history': ohlc_data.to_dict('records'),
            'trade_history': trades.to_dict('records'),
        }

        with open(filename, "w") as jsonfile:
            json.dump(data, jsonfile)

        return 1


# Extract Data and Visualization
def get_ohlc_history(symbol, timeframe, date_from, date_to, additional_columns=[]):
    ohlc = mt5.copy_rates_range(symbol, timeframe, date_from, date_to)

    ohlc_df = pd.DataFrame(ohlc)
    ohlc_df['time'] = pd.to_datetime(ohlc_df['time'], unit='s')
    return ohlc_df[['time', 'open', 'high', 'low', 'close'] + additional_columns]


def create_ohlc_fig(ohlc, name='Symbol'):
    fig = go.Figure(data=[go.Candlestick(
        name=name,
        x=ohlc['time'],
        open=ohlc['open'],
        high=ohlc['high'],
        low=ohlc['low'],
        close=ohlc['close'])])

    fig.update_layout(xaxis_rangeslider_visible=False, height=600)

    return fig


def create_price_fig(ohlc, indicators=[], height=600, title='Historical Price Data'):
    if indicators:
        fig = px.line(ohlc, x='time', y=indicators, height=600, title=title)
        fig.add_trace(go.Candlestick(x=ohlc['time'],
                                     open=ohlc['open'],
                                     high=ohlc['high'],
                                     low=ohlc['low'],
                                     close=ohlc['close'], name='OHLC Data'))
        fig.update_layout(xaxis_rangeslider_visible=False)
    else:
        fig = go.Figure(data=[go.Candlestick(x=ohlc['time'],
                                             open=ohlc['open'],
                                             high=ohlc['high'],
                                             low=ohlc['low'],
                                             close=ohlc['close'], name='OHLC Data')])

        fig.update_layout(height=height, title=title)
        fig.update_layout(xaxis_rangeslider_visible=False)

    return fig


def get_tick_history(symbol, start, end):
    ticks = mt5.copy_ticks_range(symbol, start, end, mt5.COPY_TICKS_ALL)
    ticks_df = pd.DataFrame(ticks)
    ticks_df['time'] = pd.to_datetime(ticks_df['time'], unit='s')
    ticks_df = ticks_df[['time', 'bid', 'ask']]
    return ticks_df


def evaluate_backtest(df_og):
    df = df_og.copy()
    df['open_time'] = pd.to_datetime(df['open_time'])
    df['close_time'] = pd.to_datetime(df['close_time'])

    biggest_win = df['profit'].max()
    print('biggest_profit', biggest_win)

    biggest_loss = df['profit'].min()
    print('biggest_loss', biggest_loss)

    win_trades = df[df['profit'] > 0]
    display(win_trades)

    loss_trades = df[df['profit'] < 0]
    display(loss_trades)

    avg_win = win_trades['profit'].mean()
    print('avg_win', avg_win)

    avg_loss = loss_trades['profit'].mean()
    print('avg_loss', avg_loss)

    count_profit_trades = win_trades.shape[0]
    print('count_profit_trades', count_profit_trades)

    count_loss_trades = loss_trades.shape[0]
    print('count_loss_trades', count_loss_trades)

    win_rate = count_profit_trades / count_loss_trades
    print('win_rate', round(win_rate, 2))

    rrr = abs(avg_win / avg_loss)
    print('rrr', round(rrr, 2))

    df_by_ordertype = df.groupby('order_type', as_index=False)['profit'].sum()
    display(df_by_ordertype)

    fig_ordertype = px.bar(df_by_ordertype, x='order_type', y='profit')
    display(fig_ordertype)

    df['dayofweek'] = df['close_time'].dt.dayofweek
    display(df)

    df_by_day = df.groupby('dayofweek', as_index=False)['profit'].sum()
    fig_day = px.bar(df_by_day, x='dayofweek', y='profit')
    display(fig_day)

    df['current_max'] = df['profit_cumulative'].expanding().max()
    df['drawdown'] = df['profit_cumulative'] - df['current_max']
    display(df)

    fig_drawdown = px.line(df, x='close_time', y=['profit_cumulative', 'current_max'], title='pnl curve')
    display(fig_drawdown)

    fig_drawdown2 = px.line(df, x='close_time', y='drawdown', title='drawdown curve')
    display(fig_drawdown2)

    max_drawdown = df['drawdown'].min()
    print('max_drawdown', round(max_drawdown, 2))
