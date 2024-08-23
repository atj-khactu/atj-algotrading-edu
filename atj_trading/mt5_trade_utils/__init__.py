import MetaTrader5 as mt5
import pandas as pd


# function to send a market order
def send_market_order(symbol, volume, order_type, sl=0.0, tp=0.0,
                      deviation=20, comment='', magic=0, type_filling=mt5.ORDER_FILLING_IOC):
    tick = mt5.symbol_info_tick(symbol)

    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": type_filling,
    }

    order_result = mt5.order_send(request)

    return order_result


def close_position(position, deviation=20, magic=0, comment='', type_filling=mt5.ORDER_FILLING_IOC):
    order_type_dict = {
        0: mt5.ORDER_TYPE_SELL,
        1: mt5.ORDER_TYPE_BUY
    }

    price_dict = {
        0: mt5.symbol_info_tick(position['symbol']).bid,
        1: mt5.symbol_info_tick(position['symbol']).ask
    }

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": position['ticket'],  # select the position you want to close
        "symbol": position['symbol'],
        "volume": position['volume'],  # FLOAT
        "type": order_type_dict[position['type']],
        "price": price_dict[position['type']],
        "deviation": deviation,  # INTERGER
        "magic": magic,  # INTERGER
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": type_filling,
    }

    print(request)

    order_result = mt5.order_send(request)
    return (order_result)


def close_all_positions(order_type, magic=None, type_filling=mt5.ORDER_FILLING_IOC):
    order_type_dict = {
        'buy': 0,
        'sell': 1
    }

    if mt5.positions_total() > 0:
        positions = mt5.positions_get()

        positions_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())

        # filtering by magic if specified
        if magic:
            positions_df = positions_df[positions_df['magic'] == magic]

        if order_type != 'all':
            positions_df = positions_df[(positions_df['type'] == order_type_dict[order_type])]

        if positions_df.empty:
            print('No open positions')
            return []

        results = []
        for i, position in positions_df.iterrows():
            order_result = close_position(position, type_filling=type_filling)
            print('order_result: ', order_result)
            results.append(order_result)

        return 1


def modify_sl_tp(ticket, stop_loss, take_profit):
    # modify SL/TP

    stop_loss = float(stop_loss)
    take_profit = float(take_profit)


    request = {
        'action': mt5.TRADE_ACTION_SLTP,
        'position': ticket,
        'sl': stop_loss,
        'tp': take_profit
    }

    res = mt5.order_send(request)
    return res


def get_positions(magic=None):
    if mt5.positions_total():
        positions = mt5.positions_get()
        positions_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())

        if magic:
            positions_df = positions_df[positions_df['magic'] == magic]

        return positions_df

    else:
        return pd.DataFrame(columns=['ticket', 'time', 'time_msc', 'time_update', 'time_update_msc', 'type',
                                     'magic', 'identifier', 'reason', 'volume', 'price_open', 'sl', 'tp',
                                     'price_current', 'swap', 'profit', 'symbol', 'comment', 'external_id'])
