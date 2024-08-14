import MetaTrader5 as mt5
from time import sleep

from mt5_credentials import login, passed, server, mt5_path
from atj_trading.mt5_trade_utils import send_market_order, close_all_positions


if __name__ == '__main__':
    # initialize and login to MetaTrader5
    mt5.initialize()

    # Click here to open your own trading account at Tickmill
    # https://bit.ly/4dtsz1Q
    login = 25131017
    password = 'vT8.iqYHWia!'
    server = 'TickmillEU-Demo'

    mt5.login(login, password, server)

    sleep(5)

    symbol = 'EURUSD'
    volume = 1.0
    order_type = 'buy'

    send_market_order(symbol, volume, order_type)

    sleep(5)

    close_all_positions('all')