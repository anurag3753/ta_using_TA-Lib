import json
import yfinance as yf

class StockReader:
    def __init__(self, input_filename):
        self.input_filename = input_filename

    def read_stock_list(self):
        """
        Read a list of stocks from a text file.

        Returns:
            list: A list of stock symbols.
        """
        stocks_list = []
        with open(self.input_filename, "r") as f:
            data = f.readlines()

        for stock in data:
            stock = stock.strip()
            if stock:
                stocks_list.append(stock)
        return stocks_list

    def get_stock_quotes(self, stocks_list, start_date, end_date=None):
        """
        Get historical stock quotes for a list of stocks.

        Args:
            stocks_list (list): A list of stock symbols.
            start_date (str): Start date in the format "yyyy-mm-dd".
            end_date (str, optional): End date in the format "yyyy-mm-dd". Defaults to None.

        Returns:
            dict: A dictionary containing stock quotes for each stock symbol.
        """
        if end_date is None:
            end_date = dt.datetime.now().strftime("%Y-%m-%d")

        stock_quotes = {}
        for stock in stocks_list:
            try:
                df = yf.download(stock, start=start_date, end=end_date, progress=False)
                stock_quotes[stock] = df
            except Exception as e:
                print(f"Failed to fetch quotes for {stock}: {e}")
        return stock_quotes

# Usage example
if __name__ == "__main__":
    # Create StockReader instance
    input_filename = "stocks.txt"  # Replace with actual filename
    reader = StockReader(input_filename)

    # Read stocks list
    stocks_list = reader.read_stock_list()

    # Get stock quotes
    start_date = "2022-01-01"
    end_date = "2022-12-31"
    stock_quotes = reader.get_stock_quotes(stocks_list, start_date, end_date)

