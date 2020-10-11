import datetime as dt
import pandas_datareader.data as web
import pandas as pd
from collections import OrderedDict
import talib
import pprint
import trendln
import matplotlib.pyplot as plt

# Select the time-period
start = dt.datetime(2015, 1, 1)
end = dt.datetime.now()

stocks_list = set()
with open("stocks_universe.txt", "r") as f:
    data = f.readlines()

# Stocks of interest
for stock in data:
    stock = stock.strip()
    if stock:
        stocks_list.add(stock.strip())
stocks_list = list(stocks_list)

# Read the stock quotes
failed_to_read = []
# stocks_list = ['INOXLEISUR.NS', 'TCS.NS']
candles_dict = {
    "CDLCLOSINGMARUBOZU" : talib.CDLCLOSINGMARUBOZU,
    "CDLKICKINGBYLENGTH" : talib.CDLKICKINGBYLENGTH,
    "CDLMARUBOZU" : talib.CDLMARUBOZU,
    "CDLSPINNINGTOP" : talib.CDLSPINNINGTOP,
    "CDLDOJI" : talib.CDLDOJI,
    "CDLHAMMER" : talib.CDLHAMMER,
    "CDLHANGINGMAN" : talib.CDLHANGINGMAN,
    "CDLENGULFING" : talib.CDLENGULFING,
    "CDLHARAMI" : talib.CDLHARAMI,
    "CDLPIERCING" : talib.CDLPIERCING,
    "CDL3INSIDE" : talib.CDL3INSIDE,
    "CDL3WHITESOLDIERS" : talib.CDL3WHITESOLDIERS,
    "CDLINVERTEDHAMMER" : talib.CDLINVERTEDHAMMER,
}

candles_dict_exceptions = {
    # these 2 needs other components as penetration=0
    "CDLMORNINGSTAR" : talib.CDLMORNINGSTAR,
    # "CDLEVENINGSTAR" : talib.CDLEVENINGSTAR,
    # "CDLDARKCLOUDCOVER" : talib.CDLDARKCLOUDCOVER,
}

stock_analysis = OrderedDict()
for stock in stocks_list:
    try:
        df = web.DataReader(stock, 'yahoo', start, end)
        open = df['Open']
        high = df['High']
        low = df['Low']
        close = df['Close']
        volume = df['Volume']
        stock_analysis[stock] = OrderedDict()
        stock_analysis[stock]['CMP'] =  close.iloc[-1]
        stock_analysis[stock]['CANDLES'] = OrderedDict()
        stock_analysis[stock]['INDICATORS'] = OrderedDict()
        stock_analysis[stock]['VOLUME'] = OrderedDict()
        # Run Various Candles
        for candle, candle_fun in candles_dict.items():
            val = candle_fun(open, high, low, close).iloc[-1]
            if val:
                stock_analysis[stock]['CANDLES'][candle] = val
        # Morning Star and Evening Star Candles
        for candle, candle_fun in candles_dict_exceptions.items():
            val = candle_fun(open, high, low, close, penetration=0).iloc[-1]
            if val:
                stock_analysis[stock]['CANDLES'][candle] = val

        ### Volume Indicators
        sma_vol_10_avg = talib.SMA(volume[:-1], timeperiod=10).iloc[-1]
        stock_analysis[stock]['VOLUME']['SMA_SIGNAL'] = volume.iloc[-1] > sma_vol_10_avg and close.iloc[-1] > close.iloc[-2]
        # stock_analysis[stock]['VOLUME']['ADOSC'] = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10).iloc[-1]
        stock_analysis[stock]['INDICATORS']['RSI'] = talib.RSI(close, timeperiod=14).iloc[-1]
        macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        stock_analysis[stock]['INDICATORS']['MACD'] = macdsignal.iloc[-1]
        upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        stock_analysis[stock]['INDICATORS']['BBANDS'] = {
            'upper' : upper.iloc[-1],
            'middle': middle.iloc[-1],
            'lower' : lower.iloc[-1]
        }
         

        # print(stock, ":", str(df.tail(1)))
    except Exception as e:
        failed_to_read.append(stock)
        pass
print("Failed : ", str(failed_to_read))

# with open("analysis.txt", "w") as f:
pp = pprint.PrettyPrinter(indent=4)

for stock, indicators in stock_analysis.items():
    if not indicators['CANDLES'] or indicators['VOLUME']['SMA_SIGNAL'] == False:
        continue
    print("**************************************************************")
    print("stock is : ", stock)
    pp.pprint(indicators)
print("**************************************************************")

        # f.write(stock + ": \n\n\n")
        # f.writelines(str(indicators) + "\n\n\n")