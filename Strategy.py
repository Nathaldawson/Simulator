import pandas as pd

class Strategy:
    def __init__(self, portfolio):
        self.portfolio = portfolio

    def generate_signals(self, date, rows):
        raise NotImplementedError("Subclasses must implement this method")

class MovingAverageStrategy(Strategy):
    def __init__(self, portfolio, short_window=10, long_window=30, tickers=['SWIGGY.NS']):
        super().__init__(portfolio)
        self.short_window = short_window
        self.long_window = long_window
        self.prices = {ticker: [] for ticker in tickers}
        self.invested = {ticker: False for ticker in tickers}
        self.tickers = tickers

    def generate_signals(self, date, rows):
        for symbol in self.tickers:
            if symbol not in rows:
                continue
            row = rows[symbol]

            # Always update price history on every tick
            self.prices[symbol].append(row['Close'])
            if len(self.prices[symbol]) > self.long_window * 2:
                self.prices[symbol] = self.prices[symbol][-self.long_window * 2:]

            if len(self.prices[symbol]) < self.long_window:
                continue

            temp_prices = pd.Series(self.prices[symbol])
            short_ma = temp_prices.rolling(window=self.short_window).mean().iloc[-1]
            long_ma = temp_prices.rolling(window=self.long_window).mean().iloc[-1]

            if short_ma > long_ma and not self.invested[symbol]:
                price = row['Close']
                # Invest a fixed percentage of available cash per stock, or manage allocation differently
                cash_to_invest = self.portfolio.cash * 0.05 # Example: 5% of cash per stock
                quantity_to_buy = int(cash_to_invest // price)

                if quantity_to_buy > 0 and self.portfolio.buy(symbol, quantity_to_buy, price, date=date):
                    print(f"{date}: BUY signal for {quantity_to_buy} shares of {symbol} at {price:.2f}")
                    self.invested[symbol] = True

            elif short_ma < long_ma and self.invested[symbol]:
                price = row['Close']
                quantity_to_sell = self.portfolio.positions.get(symbol, 0)

                if quantity_to_sell > 0 and self.portfolio.sell(symbol, quantity_to_sell, price, date=date):
                    print(f"{date}: SELL signal for {quantity_to_sell} shares of {symbol} at {price:.2f}")
                    self.invested[symbol] = False

class BuyAndHoldStrategy(Strategy):
    def __init__(self, portfolio, tickers=['SWIGGY.NS']):
        super().__init__(portfolio)
        self.bought = {ticker: False for ticker in tickers}
        self.tickers = tickers

    def generate_signals(self, date, rows):
        for symbol in self.tickers:
            if symbol not in rows:
                continue
            row = rows[symbol]

            if not self.bought[symbol]:
                price = row['Close']
                # Invest a fixed percentage of initial cash per stock
                cash_to_invest = self.portfolio.initial_cash * 0.05 # Example: 5% of initial cash per stock
                quantity_to_buy = int(cash_to_invest // price)
                if quantity_to_buy > 0 and self.portfolio.buy(symbol, quantity_to_buy, price, date=date):
                    print(f"{date}: BUY signal for {quantity_to_buy} shares of {symbol} at {price:.2f}")
                    print(f"{date}: BUY and HOLD: Bought {quantity_to_buy} shares of {symbol} at {price:.2f}")
                    self.bought[symbol] = True

class MomentumStrategy(Strategy):
    def __init__(self, portfolio, lookback_period=20, tickers=['SWIGGY.NS']):
        super().__init__(portfolio)
        self.lookback_period = lookback_period
        self.prices = {ticker: [] for ticker in tickers}
        self.invested = {ticker: False for ticker in tickers}
        self.tickers = tickers

    def generate_signals(self, date, rows):
        for symbol in self.tickers:
            if symbol not in rows:
                continue
            row = rows[symbol]

            self.prices[symbol].append(row['Close'])
            if len(self.prices[symbol]) > self.lookback_period * 2:
                self.prices[symbol] = self.prices[symbol][-self.lookback_period * 2:]

            if len(self.prices[symbol]) < self.lookback_period:
                continue

            current_price = row['Close']
            past_price = self.prices[symbol][-(self.lookback_period + 1)] # Price at the start of lookback period

            momentum = (current_price - past_price) / past_price

            # Simple momentum: buy if positive momentum, sell if negative
            if momentum > 0 and not self.invested[symbol]:
                price = current_price
                cash_to_invest = self.portfolio.cash * 0.05
                quantity_to_buy = int(cash_to_invest // price)

                if quantity_to_buy > 0 and self.portfolio.buy(symbol, quantity_to_buy, price, date=date):
                    print(f"{date}: BUY signal (Momentum) for {quantity_to_buy} shares of {symbol} at {price:.2f}")
                    self.invested[symbol] = True

            elif momentum < 0 and self.invested[symbol]:
                price = current_price
                quantity_to_sell = self.portfolio.positions.get(symbol, 0)

                if quantity_to_sell > 0 and self.portfolio.sell(symbol, quantity_to_sell, price, date=date):
                    print(f"{date}: SELL signal (Momentum) for {quantity_to_sell} shares of {symbol} at {price:.2f}")
                    self.invested[symbol] = False