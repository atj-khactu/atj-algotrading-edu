"""Drafting a Trading Bot class to simplify trading in Python and MT5"""

import MetaTrader5 as mt5
from time import sleep


class TradingBot:
    def __init__(self, symbol, timeframe, magic=None):
        if magic is None:
            print('Please set Magic number')
            raise ValueError

        self.symbol = symbol
        self.timeframe = timeframe

        self.trading_allowed = False
        self.update_interval = 0.1

        self.last_bar = None
        self.bar_timeout = 60

    def on_init(self):
        pass

    def on_shutdown(self):
        pass

    def on_bar(self):
        pass

    def check_new_bar(self):
        pass

    def run(self):
        while self.trading_allowed:
            is_new_bar = self.check_new_bar()

            if is_new_bar:
                self.on_bar()
                is_new_bar = False

        sleep(self.update_interval)
