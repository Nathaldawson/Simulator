import yfinance as yf
import os
import pandas as pd

def load_stock_data(ticker, interval, start_date=None, end_date=None):
    """
    Downloads historical stock data from Yahoo Finance.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'SWIGGY', 'SWIGGY.NS').
        interval (str): The data interval (e.g., '1m', '5m', '1h', '1d', '1wk', '1mo').
        start_date (str, optional): Start date for historical data (YYYY-MM-DD). Defaults to None.
        end_date (str, optiona  l): End date for historical data (YYYY-MM-DD). Defaults to None.

    Returns:
        pandas.DataFrame: Historical stock data.
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("data_loader")
    logger.info(f"Downloading data for {ticker} at {interval} interval...")

    # Append .NS for Indian stocks if no domain is specified and it's not an index
    if '.' not in ticker and not ticker.startswith('^'):
        ticker = f"{ticker}.NS"

    # Only set period if start_date and end_date are not provided
    period = None
    if not start_date and not end_date:
        if interval in ['1d', '5d', '1wk', '1mo', '3mo']:
            period = "5y"
        else:
            period = "60d" # Default to 60 days for intraday intervals

    try:
        if period:
            stock_data = yf.download(ticker, start=start_date, end=end_date, interval=interval, period=period)
        else:
            stock_data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        
        if stock_data.empty:
            logger.warning(f"No data found for ticker {ticker} with interval {interval}.")
            return pd.DataFrame()

        # Handle potential MultiIndex columns from yfinance
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = stock_data.columns.droplevel(1) # Drop the second level (e.g., 'Adj Close')

        # Rename columns to match expected format (Open, High, Low, Close, Volume)
        stock_data.columns = [col.capitalize() for col in stock_data.columns]
        stock_data = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']]
        stock_data.index.name = 'Date'
        
        logger.info(f"Data downloaded successfully for {ticker}.")
        return stock_data
    except Exception as e:
        logger.error(f"Error downloading data for {ticker}: {e}")
        return pd.DataFrame()
