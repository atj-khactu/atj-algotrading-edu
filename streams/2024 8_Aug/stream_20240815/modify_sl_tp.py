import MetaTrader5 as mt5

from projects.atj_trading_legacy.mt5_trade_utils import modify_sl_tp
from config import mt5_credentials


if __name__ == '__main__':
    # initialize and login to MetaTrader5
    mt5.initialize(mt5_credentials['exe_path'])

    # Click here to open your own trading_bots account at Tickmill
    # https://bit.ly/4dtsz1Q
    login = mt5_credentials['login']
    password = mt5_credentials['password']
    server = mt5_credentials['server']

    modify_sl_tp(49445241, 1.0, 20000.0)