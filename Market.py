
import pandas as pd
from data_loader import load_stock_data

class Market:
    def __init__(self, tickers, interval, start_date=None, end_date=None, benchmark_ticker='^NSEI'):
        if not isinstance(tickers, list):
            tickers = [tickers] # Ensure tickers is always a list
        self.tickers = tickers
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date
        self.data = self._load_all_data()
        if self.data.empty:
            raise ValueError(f"Could not load data for {tickers} with interval {interval}")
        self.current_tick = 0
        self.benchmark_data = self.load_benchmark_data(benchmark_ticker, interval, start_date, end_date)

    def _load_all_data(self):
        all_data = {}
        for ticker in self.tickers:
            stock_data = load_stock_data(ticker, self.interval, self.start_date, self.end_date)
            if not stock_data.empty:
                all_data[ticker] = stock_data
            else:
                print(f"Warning: No data loaded for {ticker}.")
        
        if not all_data:
            return pd.DataFrame()

        # Merge all dataframes on their index (Date)
        # Use outer join to keep all dates, fill missing values if necessary
        merged_data = pd.concat(all_data.values(), axis=1, keys=all_data.keys())
        merged_data.index.name = 'Date'
        return merged_data

    def get_next_tick(self):
        """
        Returns the next available price data for all tickers (as a tuple: date, dictionary of rows).
        Returns None, None if there is no more data.
        """
        if self.current_tick < len(self.data):
            date = self.data.index[self.current_tick]
            # Extract row for each ticker
            current_rows = {ticker: self.data[ticker].loc[date] for ticker in self.tickers if ticker in self.data.columns.levels[0]}
            self.current_tick += 1
            return date, current_rows
        return None, None

    def get_current_prices(self):
        """
        Returns the 'Close' prices of the current tick for all tickers as a dictionary {symbol: price}.
        """
        if self.current_tick > 0 and self.current_tick <= len(self.data):
            current_prices = {}
            for ticker in self.tickers:
                if ticker in self.data.columns.levels[0]:
                    current_prices[ticker] = self.data[ticker].iloc[self.current_tick - 1]['Close']
            return current_prices
        return {}

    def load_benchmark_data(self, ticker, interval, start_date, end_date):
        """
        Loads benchmark data.
        """
        print(f"Loading benchmark data for {ticker}...")
        benchmark_data = load_stock_data(ticker, interval, start_date, end_date)
        if benchmark_data.empty:
            print(f"Warning: Could not load benchmark data for {ticker}.")
            return None
        return benchmark_data['Close']

    def get_benchmark_price(self, date):
        """
        Returns the benchmark price for a given date.
        """
        if self.benchmark_data is not None and date in self.benchmark_data.index:
            return self.benchmark_data.loc[date]
        return None

