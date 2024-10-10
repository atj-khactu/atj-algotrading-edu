import MetaTrader5 as mt5
import pandas as pd
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'Homepage'

@app.route('/account_data')
def account_data():
    mt5.initialize()

    account_info = mt5.account_info()
    login = account_info.login
    server = account_info.server
    balance = account_info.balance
    equity = account_info.equity

    return {'login': login, 'server': server, 'balance': balance, 'equity': equity}


if __name__ == '__main__':
    app.run()