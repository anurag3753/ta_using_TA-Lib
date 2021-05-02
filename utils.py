
import talib

def is_consolidating(df, percentage=2.5):
    recent_candlesticks = df[-15:]

    max_close = recent_candlesticks['Close'].max()
    min_close = recent_candlesticks['Close'].min()

    threshold = 1 - (percentage / 100)
    if min_close > (max_close * threshold):
        return True

    return False

def is_breaking_out(df, percentage=2.5):
    last_close = df[-1:]['Close'].values[0]

    if is_consolidating(df[:-1], percentage=percentage):
        recent_closes = df[-16:-1]

        if last_close > recent_closes['Close'].max():
            return True

    return False


## Implement TTM SQUEEZE
def ttm_squeeze(df):
    df['20sma'] = df['Close'].rolling(window=20).mean()
    df['stddev'] = df['Close'].rolling(window=20).std()
    df['lower_band'] = df['20sma'] - (2 * df['stddev'])
    df['upper_band'] = df['20sma'] + (2 * df['stddev'])

    df['TR'] = abs(df['High'] - df['Low'])
    df['ATR'] = df['TR'].rolling(window=20).mean()

    df['lower_keltner'] = df['20sma'] - (df['ATR'] * 1.5)
    df['upper_keltner'] = df['20sma'] + (df['ATR'] * 1.5)

    def in_squeeze(df):
        return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

    df['squeeze_on'] = df.apply(in_squeeze, axis=1)

    if df.iloc[-3]['squeeze_on'] and df.iloc[-1]['squeeze_on']:
        return True, False
    elif df.iloc[-3]['squeeze_on'] and not df.iloc[-1]['squeeze_on']:
        return True, True
    else:
        return False, False


## Implement ATR
def cal_atr(df, timeperiod=14):
    atr = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=timeperiod)
    return atr

## Implement Super trend Indicator
def super_trend(df, timeperiod=14, multiplier=3):
    atr = cal_atr(df, timeperiod=timeperiod)
    df['upperband'] = ((df['High'] + df['Low']) / 2 ) + (multiplier * atr)
    df['lowerband'] = ((df['High'] + df['Low']) / 2 ) - (multiplier * atr)
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['Close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['Close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]
            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]
    return df.iloc[-4]['in_uptrend'], df.iloc[-1]['in_uptrend']

