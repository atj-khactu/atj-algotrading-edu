from __init__ import Orders

def on_bar(data, trades):
    o = Orders

    open_trades = trades[trades['state'] == 'open']
    num_open_trades = open_trades.shape[0]

    # entry signal
    if data['signal'] == 'buy' and not num_open_trades:
        o.open_trade('EURUSD', 1, 'buy')


    elif data['signal'] == 'sell' and not num_open_trades:
        o.open_trade('EURUSD', 1, 'sell')

    # exit signal
    if num_open_trades:
        trade = open_trades.iloc[0]
        trade_id = trade.name

        if trade['order_type'] == 'buy' and data['exit_signal'] == 'sell':
            o.close_trade(trade_id)


    return o.orders