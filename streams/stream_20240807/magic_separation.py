import MetaTrader5 as mt5
from time import sleep

from atj_trading.mt5_trade_utils import send_market_order, close_all_positions
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

    # open first position
    sleep(5)
    res = send_market_order('USDJPY', 1.0, 'buy', magic=10)

    # open second position
    sleep(5)
    send_market_order('EURJPY', 1.0, 'buy', magic=20)

    # close first position
    sleep(5)

    close_all_positions('all', magic=10)

    # close second position
    sleep(5)
    close_all_positions('all', magic=20)