"""
Open a Long position on US500 on the 1st of November and close it on the 1st of December
"""

import MetaTrader5 as mt5
from atj_algotrading.mt5_trade_utils import send_market_order, get_positions, close_all_positions
from time import sleep
from datetime import datetime

# Connect to MT5
mt5.initialize()

# Login to MT5
# mt5.login(login, password, server)


symbol = 'US500'
volume = 1.0
order_type = 'buy'

magic = 20

# Code the trading logic
trading_allowed = True
while trading_allowed:
    # Entry Logic
    if datetime.now() >= datetime(2024, 11, 1, 14, 35, 5):
        send_market_order(symbol, volume, order_type, magic=magic)

    # Exit Logic
    if datetime.now() >= datetime(2024, 12, 1, 14, 35, 5):
        close_all_positions('all', magic=magic)

    sleep(1)