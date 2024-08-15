import MetaTrader5 as mt5
from time import sleep
import pandas as pd

from mt5_credentials import login, password, server, mt5_path
from atj_trading.mt5_trade_utils import send_market_order, close_all_positions, get_positions, modify_sl_tp

"""
1) Wait for the 16:00 candle to close (1H timeframe)
2) Check whether the candle is bullish or bearish
3) Open a trade in the same direction
4) Set Stop Loss to last candle min/max
4) We close the trade at 23:00

--
Optional
1) Trailing SL using SMA/EMA
"""

symbol = 'USTEC'
timeframe = mt5.TIMEFRAME_H1
volume = 1.0
magic = 2

candle_close_start = 19
close_trades_after_hour = 19


def get_last_candle():
    candle = mt5.copy_rates_from_pos(symbol, timeframe, 1, 1)
    candle_df = pd.DataFrame(candle)
    candle_df['time'] = pd.to_datetime(candle_df['time'], unit='s')
    candle_df['hour'] = candle_df['time'].dt.hour
    return candle_df.iloc[0]


def get_candle_type(candle):
    if candle['close'] > candle['open']:
        return 'bullish candle'
    elif candle['close'] < candle['open']:
        return 'bearish candle'


if __name__ == '__main__':
    # initialize and login to MetaTrader5
    mt5.initialize()

    # Click here to open your own trading_bots account at Tickmill
    # https://bit.ly/4dtsz1Q
    mt5.login(login, password, server)

    trading_allowed = True
    while trading_allowed:
        # strategy logic
        candle = get_last_candle()

        candle_type = get_candle_type(candle)

        open_positions = get_positions(magic=magic)

        if not open_positions.empty:
            pos1 = open_positions.iloc[0]

            if pos1['type'] == mt5.ORDER_TYPE_BUY:
                if pos1['sl'] != candle['low']:
                    # update sl
                    modify_sl_tp(pos1.ticket, candle['low'], 0.0)

            elif pos1['type'] == mt5.ORDER_TYPE_sell:
                if pos1['sl'] != candle['high']:
                    # update sl
                    modify_sl_tp(pos1.ticket, candle['high'], 0.0)


        if candle['hour'] == candle_close_start and open_positions.empty:

            # buy positions
            if candle_type == 'bullish candle':
                res = send_market_order(symbol, volume, 'buy', sl=candle['low'], magic=magic)

            # sell positions
            elif candle_type == 'bearish candle':
                res = send_market_order(symbol, volume, 'sell', sl=candle['high'], magic=magic)


        """
        sleep(5)
        if candle['hour'] >= close_trades_after_hour:
            close_all_positions('all', magic=magic)
        """

        sleep(1)