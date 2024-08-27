# Please go to README.md to set up config.py

mt5_credentials = {
    'login': 1,
    'password': 'password',
    'server': 'server',
    'exe_path': None
}


def initialize_mt5():
    import MetaTrader5 as mt5

    mt5.initialize(mt5_credentials['exe_path'])
    mt5.login(mt5_credentials['login'], mt5_credentials['password'], mt5_credentials['server'])