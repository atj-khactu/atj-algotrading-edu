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


# Specify Strategy Parameters
symbol = 'DE40'
timeframe = mt5.TIMEFRAME_M1
volume = 0.1
magic = 204
comment = 'DE40 Breakout Bot'

broker_tz = pytz.timezone('EET')

atr_period = 14

trading_interval_start = time(9, 0, 0)
trading_interval_end = time(12, 59, 59)
close_trades_at = time(16, 45, 8)

def get_prev_session_high():
    d1_candle = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 1, 1)

    if d1_candle:
        # returning previous session high
        return d1_candle[0][2]


def get_last_m15_data():
    m15_candle = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 1, 1)

    if m15_candle:
        # returning close price of previous M15 close candle

        m15_candle_close = m15_candle[0][4]
        m15_candle_range = m15_candle[0][2] - m15_candle[0][3]
        return m15_candle_close, m15_candle_range


def calculate_atr():
    m15_candles = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 1, 14)
    m15_candles_df = pd.DataFrame(m15_candles)
    m15_candles_df['range'] = m15_candles_df['high'] - m15_candles_df['low']

    atr = m15_candles_df['range'].mean()
    return atr


def check_todays_breakouts():
    start_dt = datetime.now(tz=pytz.timezone('GMT+0')).replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt = datetime.now(tz=pytz.timezone('GMT+0'))

    candles = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M15, start_dt, end_dt)

    candles_df = pd.DataFrame(candles)
    candles_df['time'] = pd.to_datetime(candles_df['time'], unit='s')
    candles_df['time_hms'] = candles_df['time'].dt.time
    candles_df['prev_session_high'] = get_prev_session_high()

    def check_breakout_high(x):
        if x['open'] < x['prev_session_high'] and x['close'] > x['prev_session_high']:
            return 1  # Bullish Breakout
        else:
            return 0

    candles_df['breakout_high'] = candles_df.apply(check_breakout_high, axis=1)

    broken_out_already = candles_df[:-2]['breakout_high'].max()
    return broken_out_already


def get_signal():
    prev_session_high = get_prev_session_high()
    last_m15_close, last_m15_range = get_last_m15_data()
    atr = calculate_atr()
    broken_out_already = check_todays_breakouts()

    relative_candle_size = last_m15_range / atr

    cond1 = last_m15_close > prev_session_high
    cond2 = trading_interval_start <= datetime.now(tz=broker_tz).time() <= trading_interval_end
    cond3 = 1 <= relative_candle_size <= 3
    cond4 = broken_out_already == 0

    print('Time', datetime.now(), '|', 'Previous Session High', prev_session_high, '|',
          'Last M15 Close', last_m15_close, '|', 'Relative Candle Size', relative_candle_size,
          '|', 'Broken Out Already', broken_out_already)

    if cond1 and cond2 and cond3 and cond4:
        return 1
    else:
        return 0


def get_current_candle():
    current_candle = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)
    return current_candle[0]


if __name__ == '__main__':
    # initialize and login to MT5
    mt5.initialize()
    # mt5.login()

    # Strategy Logic
    trading_allowed = True
    current_candle_time = get_current_candle()[0]

    while trading_allowed:
        if current_candle_time < get_current_candle()[0]:

            signal = get_signal()
            open_positions = get_positions(magic=magic)

            if signal == 1 and open_positions.empty:
                order_result = send_market_order(symbol, volume, 'buy')
                print(order_result)

            current_candle_time = get_current_candle()[0]

        sleep(1)

    current_candle_time = get_current_candle()[0]



