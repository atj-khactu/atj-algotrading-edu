import MetaTrader5 as mt5
from mt5_trade_utils import get_positions, close_position

from time import sleep

if __name__ == '__main__':
    # initialize and login to MetaTrader5
    mt5.initialize()

    # Click here to open your own trading account at Tickmill
    # https://www.tickmill.com/eu
    login = 25131017
    password = 'vT8.iqYHWia!'
    server = 'TickmillEU-Demo'

    mt5.login(login, password, server)

    positions = get_positions()
    print(positions)

    sleep(5)

    for i, position in positions.iterrows():
        if position.ticket == 48035065:
            order_result = close_position(position)