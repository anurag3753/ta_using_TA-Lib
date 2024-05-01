from quotes import StockReader
from datetime import datetime
from utils import moving_average_strategy

class StockAnalyzer:
    def __init__(self, stock_quotes, category="v40"):
        self.stock_quotes = stock_quotes
        self.category = category

    def v20_strategy(self, num_days=10):
        """
        Implement the v20 strategy over the stock data.

        Args:
            num_days (int): The number of days to consider for analysis. Defaults to 10.

        Returns:
            dict: A dictionary containing strategy results for each stock symbol.
        """
        strategy_results = {}
        for stock, df in self.stock_quotes.items():
            strategy_result = self.apply_v20_strategy(df, num_days)
            strategy_results[stock] = strategy_result
        return strategy_results

    
    def apply_v20_strategy(self, df, num_days):
        """
        Apply the v20 strategy to a single stock's data.

        Args:
            df (DataFrame): The DataFrame containing stock quotes.
            num_days (int): The number of days to consider for analysis.

        Returns:
            dict: A dictionary containing buy and sell signals for the v20 strategy.
        """
        signals = []

        # Create copy to compute dma 200
        df_copy = df.copy()

        # Restrict the analysis to the last 'num_days' days of data
        df = df.tail(num_days)

        consecutive_green_candles = 0
        highest_high = None
        lowest_low = None
        unique_signals = set()

        for date, candle in df.iterrows():
            if candle["Close"] > candle["Open"]:
                consecutive_green_candles += 1

                if highest_high is None or candle["High"] > highest_high:
                    highest_high = candle["High"]
                    high_date = date # Store the date of the highest high
                if lowest_low is None or candle["Low"] < lowest_low:
                    lowest_low = candle["Low"]

                # Check if the movement from lowest low to highest high is more than 20%
                if consecutive_green_candles >= 1 and ((highest_high - lowest_low) / lowest_low) > 0.20:
                    if self.category == "v200":
                        dma_200 = moving_average_strategy(df_copy, 200)

                        if lowest_low < dma_200:
                            # Add unique buy and sell signals for the continuous green signal
                            unique_signals.add((round(lowest_low), round(highest_high), high_date))
                    else:
                        # Add unique buy and sell signals for the continuous green signal
                        unique_signals.add((round(lowest_low), round(highest_high), high_date))

            else:
                # Reset counters for red candle
                consecutive_green_candles = 0
                highest_high = None
                lowest_low = None

        # Convert unique signals to list of dictionaries
        for buy, sell, date in unique_signals:
            expected_gain = round(( sell - buy ) / buy * 100)
            signals.append({"date": date, "buy": buy, "sell": sell, "expected_gain": expected_gain})

        # Sort signals by date from highest to lowest
        signals.sort(key=lambda x: x["date"], reverse=True)

        return signals

# Usage example
if __name__ == "__main__":
    # Create StockReader instance
    input_filename = "stocks.txt"  # Replace with actual filename
    # input_filename = "C:\\Docs\\HR\\trading\\ipos\\ta_using_TA-Lib\\v40.txt"
    reader = StockReader(input_filename)

    # Read stocks list
    stocks_list = reader.read_stock_list()

    # Get stock quotes
    start_date = "2024-03-15"
    end_date = "2011-04-15"
    stock_quotes = reader.get_stock_quotes(stocks_list, start_date, end_date)

    # Create StockAnalyzer instance
    analyzer = StockAnalyzer(stock_quotes)

    # Implement strategy
    strategy_results = analyzer.v20_strategy(num_days=30)

    # Print strategy results
    print("Strategy Results:", strategy_results)