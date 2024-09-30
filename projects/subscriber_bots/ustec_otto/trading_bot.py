import MetaTrader5 as mt5
from time import sleep
import pandas as pd
from datetime import datetime, time, timedelta
import pytz

from mt5_credentials import login, password, server
from projects.atj_trading_legacy.mt5_trade_utils import send_market_order, close_all_positions, get_positions

"""
# Define trading signals
def get_signal(x):
    if (x['prev_candle_type'] == 'bullish candle' and 
        x['hour'] == 17 and 
        x['close'] > x['ema_20'] and 
        x['ema_20'] > x['ema_50']):
        return 'buy'
    elif (x['prev_candle_type'] == 'bearish candle' and 
          x['hour'] == 17 and 
          x['close'] < x['ema_20'] and 
          x['ema_20'] < x['ema_50']):
        return 'sell'
    return None

def get_exit_signal(x):
    if x['hour'] == 22:
        return 'close'
    return None
    
###

 # Entry signal
    if data['signal'] == 'buy' and not num_open_trades:
        sl = min(data['prev_low'], data['ema_20']) # Use EMA as dynamic SL
        tp = data['open'] + 2 * (data['open'] - sl) # 1:2 risk-reward ratio
        orders.open_trade(symbol, volume, 'buy', sl=sl, tp=tp)
    
    elif data['signal'] == 'sell' and not num_open_trades:
        sl = max(data['prev_high'], data['ema_20']) # Use EMA as dynamic SL
        tp = data['open'] - 2 * (sl - data['open']) # 1:2 risk-reward ratio
        orders.open_trade(symbol, volume, 'sell', sl=sl, tp=tp)
        
    # Exit signal / trail SL
    if num_open_trades:
        trade = open_trades.iloc[0]
        
        # Exit signal
        if data['exit_signal'] == 'close':
            orders.close_trade(trade)

        # Trail stop loss
        if trade['order_type'] == 'buy':
            new_sl = max(trade['sl'], data['ema_20'])
            if new_sl > trade['sl']:
                orders.modify_sl(trade, sl=new_sl)
        elif trade['order_type'] == 'sell':
            new_sl = min(trade['sl'], data['ema_20'])
            if new_sl < trade['sl']:
                orders.modify_sl(trade, sl=new_sl)

"""

symbol = 'USTEC'
timeframe = mt5.TIMEFRAME_H1
volume = 0.1
magic = 1

tz = pytz.timezone('EET')

candle_close_start = 16

update_interval_seconds = 1


def get_last_candle():
    candle = mt5.copy_rates_from_pos(symbol, timeframe, 1, 1)
    candle_df = pd.DataFrame(candle)
    candle_df['time'] = pd.to_datetime(candle_df['time'], unit='s')
    candle_df['hour'] = candle_df['time'].dt.hour
    return candle_df.iloc[0]


def get_candle_type(candle):
    if candle['close'] > candle['open']:
        return 'bullish candle'
    elif candle['close'] < candle['open']:
        return 'bearish candle'

    return 'doji'

def has_closed_trades():
    start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt = datetime.now() + timedelta(days=1)

    deals = mt5.history_deals_get(start_dt, end_dt)

    if deals:
        return True
    else:
        False


def get_ema():
    candle = mt5.copy_rates_from_pos(symbol, timeframe, 1, 50)
    candle_df = pd.DataFrame(candle)

    ema_20 = candle_df.tail(20)['close'].ewm(span=20, adjust=False).mean().iloc[-1]
    ema_50 = candle_df['close'].ewm(span=50, adjust=False).mean().iloc[-1]

    return ema_20, ema_50



if __name__ == '__main__':
    # initialize and login to MetaTrader5
    mt5.initialize()

    # Click here to open your own trading_bots account at Tickmill
    # https://bit.ly/4dtsz1Q
    mt5.login(login, password, server)

    trading_allowed = True
    while trading_allowed:
        print(datetime.now(), '|', 'US100 Momentum Bot is running')

        # strategy logic
        candle = get_last_candle()

        candle_type = get_candle_type(candle)
        open_positions = get_positions(magic=magic)

        ema_20, ema_50 = get_ema()
        print('EMA values', ema_20, ema_50)

        if candle['hour'] == candle_close_start and open_positions.empty and not has_closed_trades():

            # buy positions
            if candle_type == 'bullish candle' and ema_20 > ema_50 and candle['close'] > ema_20:
                sl = min(candle['low'], ema_20)  # Use EMA as dynamic SL
                tp = candle['close'] + 2 * (candle['close'] - sl)  # 1:2 risk-reward ratio
                res = send_market_order(symbol, volume, 'buy', sl=candle['low'], magic=magic,
                                        comment='US100 Momentum Bot')
                print(res)

            # sell positions
            elif candle_type == 'bearish candle' and ema_20 < ema_50 and candle['close'] < ema_20:
                sl = max(candle['high'], ema_20)  # Use EMA as dynamic SL
                tp = candle['close'] - 2 * (sl - candle['close'])  # 1:2 risk-reward ratio
                res = send_market_order(symbol, volume, 'sell', sl=candle['high'], magic=magic,
                                        comment='US100 Momentum Bot')
                print(res)

        # close trades before market close
        if datetime.now(tz).time() >= time(22, 55, 0):
            close_all_positions('all', magic=magic)

        """
        add Trailing Logic here
        """

        sleep(update_interval_seconds)