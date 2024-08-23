import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

from mt5_credentials import login, password, server

symbol = 'USTEC'
timeframe = mt5.TIMEFRAME_H1


def get_sma():
    candle = mt5.copy_rates_from_pos(symbol, timeframe, 1, 100)
    candle_df = pd.DataFrame(candle)

    sma_10 = candle_df.tail(10)['close'].mean()
    sma_100 = candle_df['close'].mean()

    return sma_10, sma_100


if __name__ == '__main__':
    # initialize and login to MetaTrader5
    mt5.initialize()

    # Click here to open your own trading_bots account at Tickmill
    # https://bit.ly/4dtsz1Q
    mt5.login(login, password, server)

    sma_10, sma_100 = get_sma()
    print(sma_10, sma_100)

