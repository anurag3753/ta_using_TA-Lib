import pandas as pd
import time, functools

def timer(func):
    """ Print the runtime of a decorated function """
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__!r} in {run_time:.2f} secs")
        return value
    return  wrapper_timer


def moving_average_strategy(df, window_size):
    """
    Compute moving averages for a DataFrame with given window size.

    Args:
        df (DataFrame): The DataFrame containing stock quotes.
        window_size (list): Window size for moving averages.

    Returns:
        int: Simple moving average for given window size.
    """
    df = df.sort_values(by='Date')

    column_name = f"{window_size}dma"
    df[column_name] = df['Close'].rolling(window=window_size).mean()

    # Get the current value of moving average
    current_ma = df[column_name].iloc[-1]

    try:
        current_ma = round(current_ma)
    except Exception as e:
        current_ma = 0

    return round(current_ma)


