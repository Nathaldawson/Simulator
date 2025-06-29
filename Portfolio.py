
from enum import Enum

class OrderType(Enum):
    MARKET = 1
    LIMIT = 2

class OrderStatus(Enum):
    PENDING = 1
    FILLED = 2
    CANCELLED = 3

class Order:
    def __init__(self, order_type, symbol, quantity, price, date, status=OrderStatus.PENDING):
        self.order_type = order_type
        self.symbol = symbol
        self.quantity = quantity
        self.price = price  # For limit orders, this is the limit price; for market, it's the requested price
        self.date = date
        self.status = status
        self.fill_price = None
        self.fill_quantity = 0

class FillEvent:
    def __init__(self, order, fill_price, fill_quantity, commission, date):
        self.order = order
        self.fill_price = fill_price
        self.fill_quantity = fill_quantity
        self.commission = commission
        self.date = date

class Portfolio:
    def __init__(self, initial_cash=10000, commission=0.001, slippage=0.0005, stop_loss_percentage=None, events=None):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.commission = commission
        self.slippage = slippage
        self.stop_loss_percentage = stop_loss_percentage
        self.positions = {}
        self.trades = []
        self.stop_loss_prices = {} # {symbol: stop_loss_price}
        self.pending_orders = []
        self.events = events # Event queue for communication
        self.pending_orders = []

    def get_total_value(self, current_prices):
        """
        Calculates the total value of the portfolio (cash + positions).
        `current_prices` should be a dictionary of {symbol: price}.
        """
        positions_value = 0
        for symbol, quantity in self.positions.items():
            if symbol in current_prices:
                positions_value += quantity * current_prices[symbol]
            else:
                # If a symbol's current price is not available, assume its last known price or 0
                # For a robust system, you might want to log a warning or handle this more explicitly
                print(f"Warning: Current price for {symbol} not available. Assuming 0 for total value calculation.")
        return self.cash + positions_value

    def get_position_value(self, symbol, current_price):
        """
        Calculates the value of a specific position.
        """
        if symbol in self.positions:
            return self.positions[symbol] * current_price
        return 0

    def place_order(self, order_type, symbol, quantity, price, date=None):
        order = Order(order_type, symbol, quantity, price, date)
        self.pending_orders.append(order)
        return order

    def _execute_trade(self, order, fill_price, date):
        # This is a helper method to encapsulate the actual trade execution logic
        # It's called by process_orders and check_stop_loss
        symbol = order.symbol
        quantity = order.quantity
        
        if order.order_type == OrderType.BUY:
            adjusted_price = fill_price * (1 + self.slippage)
            cost_before_commission = quantity * adjusted_price
            commission_amount = cost_before_commission * self.commission
            total_cost = cost_before_commission + commission_amount

            if self.cash >= total_cost:
                self.cash -= total_cost
                self.positions[symbol] = self.positions.get(symbol, 0) + quantity
                self.trades.append({
                    'type': 'buy',
                    'symbol': symbol,
                    'quantity': quantity,
                    'price': fill_price, # Original price
                    'adjusted_price': adjusted_price, # Price after slippage
                    'cost_before_commission': cost_before_commission,
                    'commission_amount': commission_amount,
                    'total_cost': total_cost,
                    'cash_after_trade': self.cash,
                    'date': date
                })
                if self.stop_loss_percentage is not None:
                    self.stop_loss_prices[symbol] = adjusted_price * (1 - self.stop_loss_percentage)
                order.status = OrderStatus.FILLED
                order.fill_price = adjusted_price
                order.fill_quantity = quantity
                if self.events:
                    self.events.put(FillEvent(order, adjusted_price, quantity, commission_amount, date))
                return True
            else:
                print(f"{date}: Not enough cash to buy {quantity} of {symbol} at {fill_price:.2f}")
                return False

        elif order.order_type == OrderType.SELL:
            if self.positions.get(symbol, 0) >= quantity:
                adjusted_price = fill_price * (1 - self.slippage)
                proceeds_before_commission = quantity * adjusted_price
                commission_amount = proceeds_before_commission * self.commission
                total_proceeds = proceeds_before_commission - commission_amount

                self.cash += total_proceeds
                self.positions[symbol] -= quantity
                if self.positions[symbol] == 0:
                    del self.positions[symbol]
                    if symbol in self.stop_loss_prices:
                        del self.stop_loss_prices[symbol]
                self.trades.append({
                    'type': 'sell',
                    'symbol': symbol,
                    'quantity': quantity,
                    'price': fill_price, # Original price
                    'adjusted_price': adjusted_price, # Price after slippage
                    'proceeds_before_commission': proceeds_before_commission,
                    'commission_amount': commission_amount,
                    'total_proceeds': total_proceeds,
                    'cash_after_trade': self.cash,
                    'date': date
                })
                order.status = OrderStatus.FILLED
                order.fill_price = adjusted_price
                order.fill_quantity = quantity
                if self.events:
                    self.events.put(FillEvent(order, adjusted_price, quantity, commission_amount, date))
                return True
            else:
                print(f"{date}: Not enough shares of {symbol} to sell {quantity}")
                return False
        return False

    def process_orders(self, current_prices, date):
        orders_to_remove = []
        for order in self.pending_orders:
            if order.status == OrderStatus.PENDING:
                symbol = order.symbol
                if symbol not in current_prices:
                    continue # Cannot process if price not available

                current_price = current_prices[symbol]

                if order.order_type == OrderType.MARKET:
                    # Market orders are always filled at current price
                    if self._execute_trade(order, current_price, date):
                        orders_to_remove.append(order)
                elif order.order_type == OrderType.LIMIT:
                    if order.quantity > 0: # Buy Limit
                        if current_price <= order.price:
                            if self._execute_trade(order, current_price, date):
                                orders_to_remove.append(order)
                    else: # Sell Limit (quantity < 0 for short selling, but here we assume quantity > 0 for simplicity)
                        # For a sell limit, the current price must be >= the limit price
                        if current_price >= order.price:
                            if self._execute_trade(order, current_price, date):
                                orders_to_remove.append(order)
        
        # Remove filled or cancelled orders
        self.pending_orders = [order for order in self.pending_orders if order not in orders_to_remove]

    def buy(self, symbol, quantity, price, date=None, order_type=OrderType.MARKET):
        return self.place_order(order_type, symbol, quantity, price, date)

    def sell(self, symbol, quantity, price, date=None, order_type=OrderType.MARKET):
        return self.place_order(order_type, symbol, -quantity, price, date) # Use negative quantity for sell orders internally

    def check_stop_loss(self, symbol, current_price, date=None):
        """
        Checks if stop-loss for a given symbol has been triggered.
        """
        if self.stop_loss_percentage is not None and symbol in self.positions and symbol in self.stop_loss_prices:
            if current_price <= self.stop_loss_prices[symbol]:
                print(f"{date}: STOP LOSS triggered for {symbol} at {current_price:.2f}")
                self.sell(symbol, self.positions[symbol], current_price, date=date)
                return True
        return False
