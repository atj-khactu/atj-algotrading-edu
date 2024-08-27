import MetaTrader5 as mt5
from time import sleep
import pandas as pd
from datetime import datetime

from atj_trading.mt5_trade_utils import send_market_order, get_positions
from config import mt5_credentials

if __name__ == '__main__':
    # initialize and login to MetaTrader5
    mt5.initialize(mt5_credentials['exe_path'])

    # Click here to open your own trading_bots account at Tickmill
    # https://bit.ly/4dtsz1Q
    login = mt5_credentials['login']
    password = mt5_credentials['password']
    server = mt5_credentials['server']

    mt5.login(login, password, server)

    # strategy parameters
    symbol = 'GBPUSD'
    time_frame = mt5.TIMEFRAME_M1
    period = 20
    magic = 2
    num_deviations = 1

    volume = 0.1

    # sleep to switch to MT5 platform manually to check execution
    sleep(2)

    # trade logic
    trading_allowed = True
    while trading_allowed:

        # calculate sma
        rates = mt5.copy_rates_from_pos(symbol, time_frame, 1, 20)
        rates_df = pd.DataFrame(rates)

        sma = rates_df['close'].mean()
        standard_deviation = rates_df['close'].std()
        upper_band = sma + num_deviations * standard_deviation
        lower_band = sma - num_deviations * standard_deviation

        # calculate last_close
        last_close = rates_df.iloc[-1]['close']

        print('time', datetime.now(), '|', 'sma', sma, '|', 'last_close', last_close, '|',
              'standard deviation', standard_deviation, '|', 'upper band', upper_band, '|',
              'lower band', lower_band)

        open_positions = get_positions(magic=magic)

        if last_close > upper_band and open_positions.empty:
            current_price = mt5.symbol_info_tick(symbol).bid
            sl = current_price + 1 * standard_deviation
            tp = current_price - 1 * standard_deviation

            send_market_order(symbol, volume, 'sell', magic=magic, sl=sl, tp=tp)

        elif last_close < lower_band and open_positions.empty:
            current_price = mt5.symbol_info_tick(symbol).ask
            sl = current_price - 1 * standard_deviation
            tp = current_price + 1 * standard_deviation
            send_market_order(symbol, volume, 'buy', magic=magic, sl=sl, tp=tp)

        sleep(1)