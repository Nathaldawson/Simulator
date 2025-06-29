# Sim/config.py

# --- General Simulation Settings ---
INITIAL_CASH = 100000
START_DATE = '2020-01-01'
END_DATE = '2025-06-27'
TICKERS = ['SWIGGY.NS']
INTERVAL = '1d'
BENCHMARK_TICKER = '^NSEI'

# --- Portfolio Settings ---
COMMISSION = 0.001  # 0.1%
SLIPPAGE = 0.0005 # 0.05%
STOP_LOSS_PERCENTAGE = None # e.g., 0.05 for 5%

# --- Strategy Settings ---
STRATEGY_TYPE = 'MovingAverageStrategy'

# -- MovingAverageStrategy specific --
SHORT_WINDOW = 10
LONG_WINDOW = 30

# -- MomentumStrategy specific --
LOOKBACK_PERIOD = 20

# --- Visualizer Settings ---
UPDATE_DELAY = {
    '1m': 50,
    '5m': 100,
    '1h': 150,
    '1d': 200,
    '1wk': 300,
    '1mo': 500
}
