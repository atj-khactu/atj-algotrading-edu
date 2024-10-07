import MetaTrader5 as mt5
from time import sleep
from datetime import datetime, timedelta
import pytz

symbol = 'EURUSD'
timeframe = mt5.TIMEFRAME_M1


def get_current_candle():
    current_candle = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)
    return current_candle[0]


def trading_logic():
    print(datetime.now())
    print('Trading Bot is doing something')
    print('------------------------\n')


if __name__ == "__main__":
    mt5.initialize()

    current_candle_time = get_current_candle()[0]
    while True:
        if current_candle_time < get_current_candle()[0]:
            trading_logic()

            current_candle_time = get_current_candle()[0]

        sleep(1)
