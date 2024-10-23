from flask import Flask, request
import pandas as pd
app = Flask(__name__)

@app.route('/')
def home():
    data = request.data[:-1].decode("utf-8")

    data_list = [row.split(',') for row in data.split('\n')[:-1]]
    print(data_list)

    df = pd.DataFrame(data_list, columns=['time', 'open', 'high', 'low', 'close'])
    print(df[['time', 'high', 'low']])

    print(str(df['high'].max()) + ',' + str(df['low'].min()))
    return str(df['high'].max()) + ',' + str(df['low'].min())


@app.route('/get-high-low')
def get_high_low():
    data = request.get_json()

    df = pd.DataFrame(data['ohlc'])
    print(df[['time', 'high', 'low']])

    return {'resistance': float(df['high'].max()), 'support': float(df['low'].min())}


if __name__ == '__main__':
    app.run(port=5005)