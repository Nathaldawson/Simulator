
import yfinance as yf
import os

# --- Configuration ---
# Use a BSE/NSE stock ticker. For NSE, use '.NS'; for BSE, use '.BO'.
# Example: 'SWIGGY.NS' for SWIGGY on NSE, 'SWIGGY.BO' for BSE.
TICKER = 'SWIGGY.NS'

# Date range for the historical data
START_DATE = '2020-01-01'
END_DATE = '2025-6-27'

# Output file path
OUTPUT_CSV = os.path.join('data', f"{TICKER.replace('.','_')}.csv")

# --- Data Download ---
def download_data():
    """
    Downloads historical stock data from Yahoo Finance and saves it to a CSV file.
    """
    print(f"Downloading data for {TICKER} from {START_DATE} to {END_DATE}...")
    
    # Download the data
    stock_data = yf.download(TICKER, start=START_DATE, end=END_DATE)
    
    if stock_data.empty:
        print(f"No data found for ticker {TICKER}. Please check the ticker symbol.")
        return

    # Save to CSV
    stock_data.to_csv(OUTPUT_CSV)
    print(f"Data saved successfully to {OUTPUT_CSV}")

if __name__ == '__main__':
    # Create the data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    download_data()
