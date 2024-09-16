from flask import Flask

app = Flask(__name__)
@app.route('/')
def index():
    return """
<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text">Track all markets on TradingView</span></a></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
  {
  "colorTheme": "dark",
  "dateRange": "12M",
  "showChart": false,
  "locale": "en",
  "largeChartUrl": "",
  "isTransparent": true,
  "showSymbolLogo": true,
  "showFloatingTooltip": false,
  "width": "270",
  "height": "550",
  "tabs": [
    {
      "title": "Watchlist",
      "symbols": [
        {
          "s": "FOREXCOM:SPXUSD",
          "d": "S&P 500 Index"
        },
        {
          "s": "FOREXCOM:NSXUSD",
          "d": "US 100 Cash CFD"
        },
        {
          "s": "INDEX:NKY",
          "d": "Nikkei 225"
        },
        {
          "s": "INDEX:DEU40",
          "d": "DAX Index"
        },
        {
          "s": "FX:EURUSD",
          "d": "Euro vs US Dollar"
        },
        {
          "s": "FX:USDJPY",
          "d": "US Dollar vs Japanese Yen"
        },
        {
          "s": "NASDAQ:NVDA",
          "d": "NVIDIA"
        },
        {
          "s": "KRAKEN:BTCUSD",
          "d": "Bitcoin"
        }
      ],
      "originalTitle": "Indices"
    }
  ]
}
  </script>
</div>
<!-- TradingView Widget END -->
"""


if __name__ == '__main__':
    app.run(port=8052)