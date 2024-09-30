import MetaTrader5 as mt5
from projects.atj_trading_legacy.mt5_trade_utils import get_positions, close_position

from time import sleep

if __name__ == '__main__':
    # initialize and login to MetaTrader5
    mt5.initialize()

    # Click here to open your own trading_bots account at Tickmill
    # https://bit.ly/4dtsz1Q
    login = 25131017
    password = 'vT8.iqYHWia!'
    server = 'TickmillEU-Demo'

    mt5.login(login, password, server)

    positions = get_positions()
    print(positions)

    pos_id = 48037277
    pos = positions[positions['ticket'] == pos_id].iloc[0].to_dict()

    sleep(5)
    result = close_position(pos)
    print(result)