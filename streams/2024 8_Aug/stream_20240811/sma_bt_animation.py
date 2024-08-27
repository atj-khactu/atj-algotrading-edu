from projects.backtest_simulator.backtest_simulator import create_app

app = create_app('sma_backtest.json', strategy_name='SMA Strategy')


if __name__ == '__main__':
    app.run()