import MetaTrader5 as mt5
from time import sleep
import pandas as pd
from datetime import datetime, time
import pytz

from mt5_credentials import login, password, server, mt5_path
from atj_trading.mt5_trade_utils import send_market_order, close_all_positions, get_positions, modify_sl_tp

"""
1) Wait for the 16:00 candle to close (1H timeframe)
2) Check whether the candle is bullish or bearish
3) Open a trade in the same direction
4) Set Stop Loss to last candle min/max
4) We close the trade at 22:55

--
Optional
1) Trailing SL using SMA/EMA
"""

symbol = 'USTEC'
timeframe = mt5.TIMEFRAME_H1
volume = 0.1
magic = 1

tz = pytz.timezone('EET')

candle_close_start = 16
close_trades_after_hour = 22

update_interval_seconds = 1


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
        print(datetime.now(), '|', 'US100 Momentum Bot is running')

        # strategy logic
        candle = get_last_candle()

        candle_type = get_candle_type(candle)
        open_positions = get_positions(magic=magic)

        if candle['hour'] == candle_close_start and open_positions.empty:

            # buy positions
            if candle_type == 'bullish candle':
                res = send_market_order(symbol, volume, 'buy', sl=candle['low'], magic=magic,
                                        comment='US100 Momentum Bot')
                print(res)

            # sell positions
            elif candle_type == 'bearish candle':
                res = send_market_order(symbol, volume, 'sell', sl=candle['high'], magic=magic,
                                        comment='US100 Momentum Bot')
                print(res)

        # close trades before market close
        if datetime.now(tz).time() >= time(22, 55, 0):
            close_all_positions('all', magic=magic)

        sleep(update_interval_seconds)