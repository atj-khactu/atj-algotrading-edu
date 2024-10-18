"""
1) DE40 Trading Bot on M15 that trades between 9:00 and 12:59
2) Enter a Breakout Trade whenever price closes above previous session High
3) The Breakout must be the first breakout of the session
4) The relative candle size must be between 1-3
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, time, timedelta
from time import sleep
from atj_algotrading.mt5_trade_utils import send_market_order, close_all_positions, get_positions
import pytz
from mt5_credentials import login, password, server, mt5_path


# Specify Strategy Parameters
symbol = 'US30.cash'
timeframe = mt5.TIMEFRAME_M1
hl_timeframe = mt5.TIMEFRAME_M5
volume = 1.0
magic = 301
comment = 'US30 Breakout Bot'

broker_tz = pytz.timezone('EET')

price_deviation_tolerance = 10
sr_period = 6
min_breakout_distance = 5


def get_current_candle():
    current_candle = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)
    return current_candle[0]

def get_last_closed_candle():
    current_candle = mt5.copy_rates_from_pos(symbol, timeframe, 1, 1)
    return current_candle[0]

def get_daily_highs_lows():
    ohlc_d1 = mt5.copy_rates_from_pos(symbol, hl_timeframe, 1, sr_period)
    ohlc_d1_df = pd.DataFrame(ohlc_d1)

    return ohlc_d1_df['high'].tolist(), ohlc_d1_df['low'].tolist()


def analyze_resistance_zones(prev_highs):
    prev_highs.sort(reverse=True)
    sorted_highs = prev_highs

    high1 = sorted_highs[0]
    high2 = sorted_highs[1]

    return high1 if high1 - high2 < price_deviation_tolerance else None


def analyze_support_zones(prev_lows):
    prev_lows.sort()
    sorted_lows = prev_lows

    low1 = sorted_lows[0]
    low2 = sorted_lows[1]

    return low1 if low2 - low1 < price_deviation_tolerance else None


def get_signal():
    highs, lows = get_daily_highs_lows()

    resistance = analyze_resistance_zones(highs)
    support = analyze_support_zones(lows)

    print('Highs', highs)
    print('Lows', lows)

    last_closed_candle = get_last_closed_candle()
    open_price = last_closed_candle[1]
    close_price = last_closed_candle[4]

    print('Current Time:', datetime.now(broker_tz), '|', 'Resistance:', resistance, '|', 'Support', support, '|',
          'Open Price:', open_price, '|', 'Close Price:', close_price)

    print('----------------------------------------\n')

    if resistance:
        if open_price < resistance and resistance + min_breakout_distance < close_price:
            return 1
    elif support:
        if open_price > support and support - min_breakout_distance > close_price:
            return -1


if __name__ == '__main__':
    # initialize and login to MT5
    mt5.initialize()
    # mt5.login(login, password, server)

    # Strategy Logic
    current_candle_time = 0
    trading_allowed = True

    while trading_allowed:
        if current_candle_time < get_current_candle()[0]:

            signal = get_signal()
            open_positions = get_positions(magic=magic)

            if signal == 1 and open_positions.empty:
                order_result = send_market_order(symbol, volume, 'buy', magic=magic)
                print(order_result)
            elif signal == -1 and open_positions.empty:
                order_result = send_market_order(symbol, volume, 'sell', magic=magic)
                print(order_result)

            current_candle_time = get_current_candle()[0]

        sleep(1)

    current_candle_time = get_current_candle()[0]



