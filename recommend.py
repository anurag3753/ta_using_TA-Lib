import datetime as dt
import pandas_datareader.data as web
import pandas as pd
from collections import OrderedDict
import yfinance as yf

import talib
import pprint
import sys
from utils import is_consolidating, is_breaking_out, ttm_squeeze, super_trend
from holdings import my_holdings

# Read Sys argv params (i/p filename, start date for analysis)
input_filename = sys.argv[1]
#input_filename = "test.txt"
# format of yyyy-mm-dd
# startdate = sys.argv[2]
startdate = "2022-01-01"

# Select the time-period
# start = dt.datetime(2019, 1, 1)
start = dt.datetime.strptime(startdate, "%Y-%m-%d")
end = dt.datetime.now()

stocks_list = set()
with open(input_filename, "r") as f:
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
    "CDLCLOSINGMARUBOZU": talib.CDLCLOSINGMARUBOZU,
    "CDLKICKINGBYLENGTH": talib.CDLKICKINGBYLENGTH,
    "CDLMARUBOZU": talib.CDLMARUBOZU,
    "CDLSPINNINGTOP": talib.CDLSPINNINGTOP,
    "CDLDOJI": talib.CDLDOJI,
    "CDLHAMMER": talib.CDLHAMMER,
    "CDLHANGINGMAN": talib.CDLHANGINGMAN,
    "CDLENGULFING": talib.CDLENGULFING,
    "CDLHARAMI": talib.CDLHARAMI,
    "CDLPIERCING": talib.CDLPIERCING,
    "CDL3INSIDE": talib.CDL3INSIDE,
    "CDL3WHITESOLDIERS": talib.CDL3WHITESOLDIERS,
    "CDLINVERTEDHAMMER": talib.CDLINVERTEDHAMMER,
}

candles_dict_exceptions = {
    # these 2 needs other components as penetration=0
    "CDLMORNINGSTAR": talib.CDLMORNINGSTAR,
    "CDLEVENINGSTAR": talib.CDLEVENINGSTAR,
    "CDLDARKCLOUDCOVER": talib.CDLDARKCLOUDCOVER,
}

stock_analysis = OrderedDict()
for stock in stocks_list:
    try:
        df = yf.download(stock, start, end)
        open = df["Open"]
        high = df["High"]
        low = df["Low"]
        close = df["Close"]
        volume = df["Volume"]
        cur_mkt_price = round(close.iloc[-1], 2)
        stock_analysis[stock] = OrderedDict()
        stock_analysis[stock]["CMP"] = cur_mkt_price
        stock_analysis[stock]["CANDLES"] = OrderedDict()
        stock_analysis[stock]["INDICATORS"] = OrderedDict()
        stock_analysis[stock]["VOLUME"] = OrderedDict()
        stock_analysis[stock]["IS_CONSOLIDATING"] = OrderedDict()
        stock_analysis[stock]["IS_BREAKING_OUT"] = OrderedDict()
        stock_analysis[stock]["SUPERTREND"] = OrderedDict()
        stock_analysis[stock]["TTM_SQUEEZE"] = OrderedDict()

        # Run Various Candles
        for candle, candle_fun in candles_dict.items():
            val = round(candle_fun(open, high, low, close).iloc[-1], 2)
            if val:
                stock_analysis[stock]["CANDLES"][candle] = val
        # Morning Star and Evening Star Candles
        for candle, candle_fun in candles_dict_exceptions.items():
            val = round(
                candle_fun(open, high, low, close, penetration=0).iloc[-1], 2
            )
            if val:
                stock_analysis[stock]["CANDLES"][candle] = val

        ### Volume Indicators
        sma_vol_10_avg = talib.SMA(volume[:-1], timeperiod=10).iloc[-1]
        good_vol = volume.iloc[-1] > (sma_vol_10_avg * 1.3)
        vol_long = good_vol and close.iloc[-1] > close.iloc[-2]
        vol_short = good_vol and close.iloc[-1] < close.iloc[-2]
        stock_analysis[stock]["VOLUME"]["SMA_SIGNAL"] = good_vol and (
            vol_long or vol_short
        )
        # stock_analysis[stock]['VOLUME']['SMA_SIGNAL'] = volume.iloc[-1] > sma_vol_10_avg and close.iloc[-1] > close.iloc[-2]
        ### Suggestion of 50 days SMA to be check against current price for swing trading :- Kunal Saraogi
        sma_price_50_avg = talib.SMA(close[:-1], timeperiod=50).iloc[-1]

        # is_consolidating and is_breaking_out
        stock_analysis[stock]["IS_CONSOLIDATING"] = is_consolidating(
            df, percentage=2.5
        )
        stock_analysis[stock]["IS_BREAKING_OUT"] = is_breaking_out(
            df, percentage=2.5
        )


        # Moving Average Confirmation
        ema_21 = talib.EMA(close, timeperiod=21)
        ema_55 = talib.EMA(close, timeperiod=55)
        ema_100 = talib.EMA(close, timeperiod=100)
        ema_200 = talib.EMA(close, timeperiod=200)
        stock_analysis[stock]["INDICATORS"]["EMA_SIGNAL"] = (
            (ema_21.iloc[-1] > ema_55.iloc[-1])
            and (ema_55.iloc[-1] > ema_100.iloc[-1])
            and (ema_100.iloc[-1] > ema_200.iloc[-1])
        )

        # ADX, +DI, -DI
        adx = round(talib.ADX(high, low, close, timeperiod=14).iloc[-1], 2)
        minus_di = round(
            talib.MINUS_DI(high, low, close, timeperiod=14).iloc[-1], 2
        )
        plus_di = round(
            talib.PLUS_DI(high, low, close, timeperiod=14).iloc[-1], 2
        )
        stock_analysis[stock]["INDICATORS"]["ADX_SYSTEM"] = (
            adx >= 25 and plus_di > minus_di
        )
        # Aroon Oscillator
        stock_analysis[stock]["INDICATORS"]["AROON"] = (
            round(talib.AROONOSC(high, low, timeperiod=25).iloc[-1], 2) > 0
        )

        stock_analysis[stock]["INDICATORS"]["RSI"] = round(
            talib.RSI(close, timeperiod=14).iloc[-1], 2
        )
        macd, macdsignal, macdhist = talib.MACD(
            close, fastperiod=12, slowperiod=26, signalperiod=9
        )
        stock_analysis[stock]["INDICATORS"]["MACD"] = (
            round(macdsignal.iloc[-1], 2) > 0
        )
        upper, middle, lower = talib.BBANDS(
            close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
        )
        bbands = {
            "upper": round(upper.iloc[-1], 2),
            "middle": round(middle.iloc[-1], 2),
            "lower": round(lower.iloc[-1], 2),
        }
        stock_analysis[stock]["INDICATORS"]["BBANDS"] = (
            abs(bbands["lower"] - cur_mkt_price) / bbands["lower"] < 0.02
        )

        # print(stock, ":", str(df.tail(1)))
    except Exception as e:
        failed_to_read.append(stock)
        print(e)
        pass
print("Failed : ", str(failed_to_read))

pp = pprint.PrettyPrinter(indent=4)

for stock, indicators in stock_analysis.items():
    if not indicators["CANDLES"] or indicators["VOLUME"]["SMA_SIGNAL"] == False:
        continue
    print("**************************************************************")
    print("stock is : ", stock)
    pp.pprint(indicators)
print("**************************************************************")

# f.write(stock + ": \n\n\n")
# f.writelines(str(indicators) + "\n\n\n")
