import MetaTrader5 as mt5
from time import sleep

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

    sleep(5)

    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": 'EURUSD',
        "volume": 0.1,
        "type": mt5.ORDER_TYPE_SELL_STOP_LIMIT,
        "price": 1.09,
        "stoplimit": 1.1,
        "deviation": 20,
        "magic": 0,
        "comment": "STOP LIMIT ORDER",
        "type_time": mt5.ORDER_TIME_GTC,
    }

    res = mt5.order_send(request)
    print(res)