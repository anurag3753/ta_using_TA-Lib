# Usage example
from strategy import StockAnalyzer
from quotes import StockReader
import datetime

class StockProcessor:
    def __init__(self, input_filename):
        self.input_filename = input_filename

    def process_stocks(self):
        # Read stocks list
        reader = StockReader(self.input_filename)
        # Read stocks list
        stocks_list = reader.read_stock_list()

        # Calculate the start date as one month back from today
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

        # Retrieve stock quotes using the updated dates
        stock_quotes = reader.get_stock_quotes(stocks_list, start_date, end_date)

        # Create StockAnalyzer instance
        analyzer = StockAnalyzer(stock_quotes)

        # Implement strategy
        strategy_results = analyzer.v20_strategy(num_days=30)

        # Filter out empty strategy results
        non_empty_results = {symbol: results for symbol, results in strategy_results.items() if results}

        # Print non-empty strategy results
        if non_empty_results:
            print("Non-empty Strategy Results:")
            for symbol, results in non_empty_results.items():
                print(f"{symbol}: {results}")
        else:
            print("No non-empty strategy results to display.")

if __name__ == "__main__":
    input_filename1 = "C:\\Docs\\HR\\trading\\ipos\\ta_using_TA-Lib\\v40.txt"  # Replace with actual filename
    processor1 = StockProcessor(input_filename1)
    processor1.process_stocks()

    input_filename2 = "C:\\Docs\\HR\\trading\\ipos\\ta_using_TA-Lib\\v40next.txt"  # Replace with actual filename
    processor2 = StockProcessor(input_filename2)
    processor2.process_stocks()