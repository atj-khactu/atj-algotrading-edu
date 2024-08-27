from projects.backtest_simulator.backtest_simulator import create_app

app = create_app('vwap_backtest.json', num_candles=100, candle_step=1)

if __name__ == '__main__':
    app.run()