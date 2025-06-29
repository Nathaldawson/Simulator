from Market import Market
from Portfolio import Portfolio
from Strategy import MovingAverageStrategy, BuyAndHoldStrategy

class Simulator:
    def __init__(self, tickers=["SWIGGY.NS"], interval="1d", start_date=None, end_date=None, strategy_type="MovingAverageStrategy"):
        # Configuration
        initial_cash = 100000

        # 1. Initialize components
        self.portfolio = Portfolio(initial_cash)
        self.portfolio_history = []
        self.market = None
        self.benchmark_history = []
        self.strategy = None
        self.update_market_and_strategy(tickers, interval, start_date, end_date, strategy_type)

    def update_market_and_strategy(self, tickers, interval, start_date, end_date, strategy_type):
        self.market = Market(tickers, interval, start_date, end_date)

        # Get benchmark data for analysis
        self.benchmark_history = []
        if self.market.benchmark_data is not None:
            # Align benchmark data with market data dates
            # The market data is now a MultiIndex DataFrame, so we need to adjust how we reindex
            # We'll use the first ticker's index as the reference for dates
            first_ticker_data_index = self.market.data.index
            aligned_benchmark_data = self.market.benchmark_data.reindex(first_ticker_data_index, method='ffill')
            self.benchmark_history = aligned_benchmark_data.dropna().tolist()

        if strategy_type == "MovingAverageStrategy":
            self.strategy = MovingAverageStrategy(self.portfolio, tickers=tickers)
        elif strategy_type == "BuyAndHoldStrategy":
            self.strategy = BuyAndHoldStrategy(self.portfolio, tickers=tickers)
        elif strategy_type == "MomentumStrategy":
            from Strategy import MomentumStrategy
            self.strategy = MomentumStrategy(self.portfolio, tickers=tickers)
        else:
            raise ValueError("Unknown strategy type")

    def step(self):
        """
        Perform a single simulation step (tick):
        - Advance market
        - Update portfolio value
        - Check stop-loss
        - Generate strategy signals
        Returns True if step was performed, False if at end of data.
        """
        date, rows = self.market.get_next_tick()
        if date is None:
            return False

        current_prices = self.market.get_current_prices()
        if current_prices:
            self.update_portfolio_history(current_prices)
            for symbol in list(self.portfolio.positions.keys()):
                if symbol in current_prices:
                    self.portfolio.check_stop_loss(symbol, current_prices[symbol], date=date)

        # Pass the entire row data (which is now a dictionary of rows per ticker) to the strategy
        self.strategy.generate_signals(date, rows)
        return True

    def update_portfolio_history(self, current_prices):
        if current_prices:
            total_value = self.portfolio.get_total_value(current_prices)
            self.portfolio_history.append(total_value)

    def run_simulation(self):
        while self.step():
            pass

if __name__ == '__main__':
    import tkinter as tk
    from Visualizer import Visualizer
    root = tk.Tk()
    simulator = Simulator()
    app = Visualizer(root, simulator)
    root.mainloop()
