import MetaTrader5 as mt5
import pandas as pd
from time import sleep

from mt5_trade_utils import send_market_order, close_all_positions


if __name__ == '__main__':
    # initialize and login to MetaTrader5
    mt5.initialize()

    # Click here to open your own trading account at Tickmill
    # https://www.tickmill.com/eu
    login = 25131017
    password = 'vT8.iqYHWia!'
    server = 'TickmillEU-Demo'

    mt5.login(login, password, server)

    sleep(5)
    send_market_order('EURUSD', 1.0, 'buy')
    sleep(5)
    close_all_positions('all')
