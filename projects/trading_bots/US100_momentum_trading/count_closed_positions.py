import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

from mt5_credentials import login, password, server


def has_closed_trades():
    start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    print('today', start_dt)
    end_dt = datetime.now() + timedelta(days=1)
    print('now', end_dt)

    deals = mt5.history_deals_get(start_dt, end_dt)
    print(deals)

    if deals:
        return True
    else:
        False

if __name__ == '__main__':
    # initialize and login to MetaTrader5
    mt5.initialize()

    # Click here to open your own trading_bots account at Tickmill
    # https://bit.ly/4dtsz1Q
    mt5.login(login, password, server)

    closed_trades = has_closed_trades()
    print(closed_trades)