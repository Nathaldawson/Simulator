import tkinter as tk
from tkinter import ttk
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from Analysis import Analysis
from Market import Market

class Visualizer:
    def __init__(self, root, simulator):
        self.root = root
        self.simulator = simulator
        self.root.title("Stock Market Simulator")

        # --- BLOOMBERG TERMINAL THEME (Black & Orange) ---
        # Main background: black, text: orange, accents: deep orange/yellow, controls: dark gray
        self.root.tk_setPalette(background='#101010', foreground='#FFA500',
                                activeBackground='#222222', activeForeground='#FFA500',
                                selectBackground='#333333', selectForeground='#FFA500',
                                highlightBackground='#101010', highlightForeground='#FFA500')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#101010', foreground='#FFA500')
        style.configure('TLabel', background='#101010', foreground='#FFA500', font=('Consolas', 10, 'bold'))
        style.configure('TEntry', fieldbackground='#181818', foreground='#FFA500', background='#181818', bordercolor='#FFA500', insertcolor='#FFA500')
        style.configure('TButton', background='#222222', foreground='#FFA500', bordercolor='#FFA500', focusthickness=2, focuscolor='#FFA500')
        style.map('TButton', background=[('active', '#FFA500')], foreground=[('active', '#101010')])
        style.configure('TCombobox', fieldbackground='#181818', background='#181818', foreground='#FFA500', bordercolor='#FFA500')
        style.map('TCombobox', fieldbackground=[('readonly', '#181818')], foreground=[('readonly', '#FFA500')])
        style.configure('TScale', background='#101010', troughcolor='#222222', sliderthickness=15)
        style.configure('TLabelframe', background='#101010', foreground='#FFA500', bordercolor='#FFA500')
        style.configure('TLabelframe.Label', background='#101010', foreground='#FFA500')
        style.configure('Treeview', background='#181818', fieldbackground='#181818', foreground='#FFA500', bordercolor='#FFA500')
        style.configure('TScrollbar', background='#222222', troughcolor='#181818', arrowcolor='#FFA500')
        # Set font for all widgets
        self.root.option_add('*Font', 'Consolas 10')
        # --- END BLOOMBERG THEME ---

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1) # Chart column
        main_frame.grid_columnconfigure(1, weight=0) # Controls column
        main_frame.grid_rowconfigure(0, weight=1)

        # Footer Label
        self.footer_label = ttk.Label(self.root, text="Created by Nathal Dawson", anchor="center", font=("Consolas", 9, "bold"), background="#101010", foreground="#FFA500")
        self.footer_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.root.grid_rowconfigure(1, weight=0)

        # Chart Frame
        chart_frame = ttk.Frame(main_frame)
        chart_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=5)
        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)

        # Controls and Info Frame
        right_panel_frame = ttk.Frame(main_frame, padding="5")
        right_panel_frame.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=5, pady=5)
        


        # --- Portfolio Info ---
        info_frame = ttk.LabelFrame(right_panel_frame, text="Portfolio Summary", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=5)
        info_frame.grid_columnconfigure(0, weight=1)

        self.portfolio_label = ttk.Label(info_frame, text="Portfolio Value: ₹0.00   |   Cash: ₹0.00", font=("Arial", 10, "bold"))
        self.portfolio_label.grid(row=0, column=0, padx=5, pady=2, sticky=(tk.W, tk.E))

        self.holdings_label = ttk.Label(info_frame, text="", font=("Arial", 9))
        self.holdings_label.grid(row=1, column=0, padx=5, pady=2, sticky=(tk.W, tk.E))

        self.metrics_label = ttk.Label(info_frame, text="", font=("Arial", 10, "bold"))
        self.metrics_label.grid(row=2, column=0, padx=5, pady=2, sticky=(tk.W, tk.E))

        self.var_label = ttk.Label(info_frame, text="", font=("Arial", 9))
        self.var_label.grid(row=3, column=0, padx=5, pady=2, sticky=(tk.W, tk.E))

        self.cvar_label = ttk.Label(info_frame, text="", font=("Arial", 9))
        self.cvar_label.grid(row=4, column=0, padx=5, pady=2, sticky=(tk.W, tk.E))

        # --- Data Selection ---
        data_selection_frame = ttk.LabelFrame(right_panel_frame, text="Data Selection", padding="10")
        data_selection_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), pady=5)
        data_selection_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(data_selection_frame, text="Chart Ticker:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.chart_ticker_selection = ttk.Combobox(data_selection_frame, values=[], state="readonly", width=12)
        self.chart_ticker_selection.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        

        ttk.Label(data_selection_frame, text="Tickers (comma-separated):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.ticker_entry = ttk.Entry(data_selection_frame, width=40)
        self.ticker_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.ticker_entry.insert(0, "SWIGGY.NS") # Default ticker

        self.load_data_button = ttk.Button(data_selection_frame, text="Load Data", command=self.load_data)
        self.load_data_button.grid(row=1, column=4, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(data_selection_frame, text="Interval:").grid(row=2, column=2, padx=5, pady=5, sticky=tk.E)
        self.interval_selection = ttk.Combobox(data_selection_frame,
                                               values=['1m', '5m', '10m', '15m', '30m', '1h', '3h', '6h', '12h', '1d', '1wk', '1mo', '3mo'],
                                               state="readonly")
        self.interval_selection.grid(row=2, column=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.interval_selection.set("1d")

        ttk.Label(data_selection_frame, text="Benchmark:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        self.benchmark_entry = ttk.Entry(data_selection_frame, width=12)
        self.benchmark_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.benchmark_entry.insert(0, "^NSEI")

        ttk.Label(data_selection_frame, text="Start Date (YYYY-MM-DD):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        self.start_date_entry = ttk.Entry(data_selection_frame, width=15)
        self.start_date_entry.grid(row=4, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.start_date_entry.insert(0, "2020-01-01")

        ttk.Label(data_selection_frame, text="End Date (YYYY-MM-DD):").grid(row=4, column=2, padx=5, pady=5, sticky=tk.E)
        self.end_date_entry = ttk.Entry(data_selection_frame, width=15)
        self.end_date_entry.grid(row=4, column=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.end_date_entry.insert(0, "2025-06-27")

        # --- Simulation Controls ---
        controls_frame = ttk.LabelFrame(right_panel_frame, text="Simulation Controls", padding="10")
        controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=5)
        controls_frame.grid_columnconfigure(1, weight=1)

        # Simulation control buttons
        self.running = False
        self.play_pause_button = ttk.Button(controls_frame, text="Run Simulation", command=self.toggle_play_pause)
        self.play_pause_button.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        self.reset_button = ttk.Button(controls_frame, text="Reset Simulation", command=self.reset_simulation)
        self.reset_button.grid(row=0, column=2, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        # Buy/Sell and Quantity
        action_frame = ttk.Frame(controls_frame)
        action_frame.grid(row=1, column=0, columnspan=4, pady=5, sticky=tk.W)
        self.buy_button = ttk.Button(action_frame, text="Buy", command=self.buy_stock)
        self.buy_button.pack(side=tk.LEFT, padx=5)
        self.sell_button = ttk.Button(action_frame, text="Sell", command=self.sell_stock)
        self.sell_button.pack(side=tk.LEFT, padx=5)
        self.quantity_label = ttk.Label(action_frame, text="Quantity:")
        self.quantity_label.pack(side=tk.LEFT, padx=5)
        self.quantity_entry = ttk.Entry(action_frame, width=10)
        self.quantity_entry.pack(side=tk.LEFT, padx=5)
        self.quantity_entry.insert(0, "10")

        ttk.Label(action_frame, text="Symbol:").pack(side=tk.LEFT, padx=5)
        self.trade_symbol_selection = ttk.Combobox(action_frame, values=[], state="readonly", width=10)
        self.trade_symbol_selection.pack(side=tk.LEFT, padx=5)

        # Commission, Slippage, Stop Loss
        ttk.Label(controls_frame, text="Commission (%):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.commission_entry = ttk.Entry(controls_frame, width=10)
        self.commission_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.commission_entry.insert(0, "0.1") # Default to 0.1%

        ttk.Label(controls_frame, text="Slippage (%):").grid(row=2, column=2, padx=5, pady=5, sticky=tk.E)
        self.slippage_entry = ttk.Entry(controls_frame, width=10)
        self.slippage_entry.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)
        self.slippage_entry.insert(0, "0.05") # Default to 0.05%

        ttk.Label(controls_frame, text="Stop Loss (%):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        self.stop_loss_entry = ttk.Entry(controls_frame, width=10)
        self.stop_loss_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.stop_loss_entry.insert(0, "") # Optional, no default

        # Strategy Parameters
        ttk.Label(controls_frame, text="Short Window:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        self.short_window_entry = ttk.Entry(controls_frame, width=10)
        self.short_window_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        self.short_window_entry.insert(0, "10")

        ttk.Label(controls_frame, text="Long Window:").grid(row=4, column=2, padx=5, pady=5, sticky=tk.E)
        self.long_window_entry = ttk.Entry(controls_frame, width=10)
        self.long_window_entry.grid(row=4, column=3, padx=5, pady=5, sticky=tk.W)
        self.long_window_entry.insert(0, "30")

        ttk.Label(controls_frame, text="Strategy:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.E)
        self.strategy_selection = ttk.Combobox(controls_frame,
                                               values=["MovingAverageStrategy", "BuyAndHoldStrategy", "MomentumStrategy"],
                                               state="readonly")
        self.strategy_selection.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.strategy_selection.set("MovingAverageStrategy") # Default strategy
        self.strategy_selection.bind("<<ComboboxSelected>>", self.on_strategy_selected)

        # --- Chart Figure and Axes ---
        self.fig = Figure(figsize=(12, 9), dpi=100, facecolor='#101010')
        gs = self.fig.add_gridspec(3, 1, height_ratios=[4, 1, 2])
        self.ax = self.fig.add_subplot(gs[0], facecolor='#181818')
        self.vol_ax = self.fig.add_subplot(gs[1], sharex=self.ax, facecolor='#181818')
        self.equity_ax = self.fig.add_subplot(gs[2], facecolor='#181818')
        self.ax.tick_params(axis='x', labelbottom=False, colors='#FFA500')
        self.ax.tick_params(axis='y', colors='#FFA500')
        self.vol_ax.tick_params(axis='x', labelbottom=False, colors='#FFA500')
        self.vol_ax.tick_params(axis='y', colors='#FFA500')
        self.equity_ax.tick_params(axis='x', colors='#FFA500')
        self.equity_ax.tick_params(axis='y', colors='#FFA500')
        self.fig.subplots_adjust(hspace=0.1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.load_data()

    

    def update_market_data(self, new_tickers):
        # This function will update the simulator's market data with new tickers
        # without resetting the entire simulation.
        current_interval = self.interval_selection.get()
        current_start_date = self.start_date_entry.get()
        current_end_date = self.end_date_entry.get()
        current_benchmark = self.benchmark_entry.get()

        try:
            # Create a new Market instance with the updated list of tickers
            self.simulator.market = Market(new_tickers, current_interval, current_start_date, current_end_date, benchmark_ticker=current_benchmark)
            
            # Update the strategy's tickers if it has a tickers attribute
            if hasattr(self.simulator.strategy, 'tickers'):
                self.simulator.strategy.tickers = new_tickers

            # Reset the market's current tick to re-simulate from the beginning with new data
            self.simulator.market.current_tick = 0
            self.simulator.portfolio_history = []
            self.simulator.portfolio.cash = self.simulator.portfolio.initial_cash
            self.simulator.portfolio.positions = {}
            self.simulator.portfolio.trades = []

            # Update benchmark history for analysis
            self.simulator.benchmark_history = []
            if self.simulator.market.benchmark_data is not None:
                first_ticker_data_index = self.simulator.market.data.index
                aligned_benchmark_data = self.simulator.market.benchmark_data.reindex(first_ticker_data_index, method='ffill')
                self.simulator.benchmark_history = aligned_benchmark_data.dropna().tolist()

            # Update ticker ComboBoxes for chart and trading
            if hasattr(self.simulator.market, 'data') and hasattr(self.simulator.market.data, 'columns'):
                if hasattr(self.simulator.market.data.columns, 'levels'):
                    tickers_from_data = list(self.simulator.market.data.columns.levels[0])
                else:
                    tickers_from_data = list(self.simulator.market.data.columns)
                self.chart_ticker_selection['values'] = tickers_from_data
                self.trade_symbol_selection['values'] = tickers_from_data
                if tickers_from_data:
                    self.chart_ticker_selection.set(tickers_from_data[0])
                    self.trade_symbol_selection.set(tickers_from_data[0])
            self.reset_simulation() # Reset simulation state after loading new data
        except ValueError as e:
            tk.messagebox.showerror("Error", str(e))

    def add_stock_to_tickers(self):
        # Add stock from search entry to ticker list, update chart and ComboBoxes
        new_stock = self.stock_search_entry.get().strip()
        if not new_stock:
            tk.messagebox.showerror("Error", "Please enter a stock symbol to add.")
            return
        # Add to ticker_entry if not already present
        current_tickers = [t.strip() for t in self.ticker_entry.get().split(',') if t.strip()]
        if new_stock in current_tickers:
            tk.messagebox.showinfo("Info", f"{new_stock} is already in the ticker list.")
            return
        current_tickers.append(new_stock)
        self.ticker_entry.delete(0, tk.END)
        self.ticker_entry.insert(0, ','.join(current_tickers))
        
        # Update market data with the new set of tickers
        self.update_market_data(current_tickers)
        
        # Set chart to new stock
        self.chart_ticker_selection.set(new_stock)
        self.trade_symbol_selection.set(new_stock)
        self.stock_search_entry.delete(0, tk.END)


    def load_data(self):
        tickers_str = self.ticker_entry.get()
        tickers = [t.strip() for t in tickers_str.split(',') if t.strip()]
        if not tickers:
            tk.messagebox.showerror("Error", "Please enter at least one ticker symbol.")
            return

        interval = self.interval_selection.get()
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        strategy_type = self.strategy_selection.get()

        try:
            short_window = int(self.short_window_entry.get())
        except Exception:
            short_window = 10
        try:
            long_window = int(self.long_window_entry.get())
        except Exception:
            long_window = 30
        try:
            commission = float(self.commission_entry.get()) / 100.0
        except Exception:
            commission = 0.001
        try:
            slippage = float(self.slippage_entry.get()) / 100.0
        except Exception:
            slippage = 0.0005
        try:
            stop_loss = float(self.stop_loss_entry.get()) / 100.0 if self.stop_loss_entry.get() else None
        except Exception:
            stop_loss = None

        try:
            self.simulator.__init__(tickers=tickers, interval=interval, start_date=start_date, end_date=end_date, strategy_type=strategy_type)
            self.simulator.portfolio.commission = commission
            self.simulator.portfolio.slippage = slippage
            self.simulator.portfolio.stop_loss_percentage = stop_loss
            if hasattr(self.simulator.strategy, 'short_window'):
                self.simulator.strategy.short_window = short_window
            if hasattr(self.simulator.strategy, 'long_window'):
                self.simulator.strategy.long_window = long_window
            # Update ticker ComboBoxes for chart and trading
            if hasattr(self.simulator.market, 'data') and hasattr(self.simulator.market.data, 'columns'):
                if hasattr(self.simulator.market.data.columns, 'levels'):
                    tickers_from_data = list(self.simulator.market.data.columns.levels[0])
                else:
                    tickers_from_data = list(self.simulator.market.data.columns)
                self.chart_ticker_selection['values'] = tickers_from_data
                self.trade_symbol_selection['values'] = tickers_from_data
                if tickers_from_data:
                    self.chart_ticker_selection.set(tickers_from_data[0])
                    self.trade_symbol_selection.set(tickers_from_data[0])
            self.reset_simulation()
        except ValueError as e:
            tk.messagebox.showerror("Error", str(e))

    def toggle_play_pause(self):
        self.running = not self.running
        if self.running:
            self.play_pause_button.config(text="Pause")
            self.update_chart()
        else:
            self.play_pause_button.config(text="Play")

    def stop_simulation(self):
        self.running = False
        self.play_pause_button.config(text="Play")
        # Optionally reset the chart to initial state or clear it
        self.ax.clear()
        self.vol_ax.clear()
        self.canvas.draw()

    def reset_simulation(self):
        self.running = False
        self.play_pause_button.config(text="Play")
        self.simulator.market.current_tick = 0
        self.simulator.portfolio_history = []
        self.simulator.portfolio.cash = self.simulator.portfolio.initial_cash
        self.simulator.portfolio.positions = {}
        self.simulator.portfolio.trades = []
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, "2020-01-01")
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, "2025-06-27")
        # Reset strategy's internal state for multi-ticker support
        if hasattr(self.simulator.strategy, 'prices'):
            if isinstance(self.simulator.strategy.prices, dict):
                for ticker in self.simulator.strategy.prices:
                    self.simulator.strategy.prices[ticker] = []
            else:
                self.simulator.strategy.prices = []
        if hasattr(self.simulator.strategy, 'invested'):
            if isinstance(self.simulator.strategy.invested, dict):
                for ticker in self.simulator.strategy.invested:
                    self.simulator.strategy.invested[ticker] = False
            else:
                self.simulator.strategy.invested = False
        if hasattr(self.simulator.strategy, 'bought'):
            if isinstance(self.simulator.strategy.bought, dict):
                for ticker in self.simulator.strategy.bought:
                    self.simulator.strategy.bought[ticker] = False
            else:
                self.simulator.strategy.bought = False
        self.update_chart()

    def on_strategy_selected(self, event):
        selected_strategy = self.strategy_selection.get()
        current_tickers_str = self.ticker_entry.get()
        current_tickers = [t.strip() for t in current_tickers_str.split(',') if t.strip()]
        current_interval = self.interval_selection.get()
        current_start_date = self.start_date_entry.get()
        current_end_date = self.end_date_entry.get()
        try:
            short_window = int(self.short_window_entry.get())
        except Exception:
            short_window = 10
        try:
            long_window = int(self.long_window_entry.get())
        except Exception:
            long_window = 30
        try:
            commission = float(self.commission_entry.get()) / 100.0
        except Exception:
            commission = 0.001
        try:
            slippage = float(self.slippage_entry.get()) / 100.0
        except Exception:
            slippage = 0.0005
        try:
            stop_loss = float(self.stop_loss_entry.get()) / 100.0 if self.stop_loss_entry.get() else None
        except Exception:
            stop_loss = None
        self.simulator.__init__(tickers=current_tickers, interval=current_interval, start_date=current_start_date, end_date=current_end_date, strategy_type=selected_strategy)
        self.simulator.portfolio.commission = commission
        self.simulator.portfolio.slippage = slippage
        self.simulator.portfolio.stop_loss_percentage = stop_loss
        if hasattr(self.simulator.strategy, 'short_window'):
            self.simulator.strategy.short_window = short_window
        if hasattr(self.simulator.strategy, 'long_window'):
            self.simulator.strategy.long_window = long_window
        self.reset_simulation()


    def buy_stock(self):
        try:
            quantity = int(self.quantity_entry.get())
            symbol = self.trade_symbol_selection.get()
            if not symbol:
                tk.messagebox.showerror("Error", "Please select a symbol to buy.")
                return

            current_prices = self.simulator.market.get_current_prices()
            price = current_prices.get(symbol)

            # Insert: get the current simulation date
            current_tick = self.simulator.market.current_tick
            if current_tick < len(self.simulator.market.data.index):
                current_date = self.simulator.market.data.index[current_tick]
            else:
                current_date = self.simulator.market.data.index[-1]

            if price is not None:
                commission = float(self.commission_entry.get()) / 100
                slippage = float(self.slippage_entry.get()) / 100
                stop_loss_percentage_str = self.stop_loss_entry.get()
                stop_loss_percentage = float(stop_loss_percentage_str) / 100 if stop_loss_percentage_str else None

                self.simulator.portfolio.commission = commission
                self.simulator.portfolio.slippage = slippage
                self.simulator.portfolio.stop_loss_percentage = stop_loss_percentage

                self.simulator.portfolio.buy(symbol, quantity, price, date=current_date)
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid quantity or input.")
            pass

    def sell_stock(self):
        try:
            quantity = int(self.quantity_entry.get())
            symbol = self.trade_symbol_selection.get()
            if not symbol:
                tk.messagebox.showerror("Error", "Please select a symbol to sell.")
                return

            current_prices = self.simulator.market.get_current_prices()
            price = current_prices.get(symbol)

            # Insert: get the current simulation date
            current_tick = self.simulator.market.current_tick
            if current_tick < len(self.simulator.market.data.index):
                current_date = self.simulator.market.data.index[current_tick]
            else:
                current_date = self.simulator.market.data.index[-1]

            if price is not None:
                commission = float(self.commission_entry.get()) / 100
                slippage = float(self.slippage_entry.get()) / 100
                stop_loss_percentage_str = self.stop_loss_entry.get()
                stop_loss_percentage = float(stop_loss_percentage_str) / 100 if stop_loss_percentage_str else None

                self.simulator.portfolio.commission = commission
                self.simulator.portfolio.slippage = slippage
                self.simulator.portfolio.stop_loss_percentage = stop_loss_percentage

                self.simulator.portfolio.sell(symbol, quantity, price, date=current_date)
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid quantity or input.")
            pass

    def update_chart(self):
        if not self.running:
            return

        # Use the centralized simulation step
        step_result = self.simulator.step()
        if not step_result:
            self.running = False
            self.play_pause_button.config(text="Simulation Finished")
            self.portfolio_label.config(text="Simulation Finished.")
            self.metrics_label.config(text="")
            return

        # Display the selected ticker's chart (LIVE: plot only up to current tick, no static blue line)
        if not self.simulator.market.data.empty:
            chart_ticker = self.chart_ticker_selection.get()
            if chart_ticker and chart_ticker in self.simulator.market.data.columns.levels[0]:
                ticker_data = self.simulator.market.data[chart_ticker]
                if not isinstance(ticker_data.index, pd.DatetimeIndex):
                    ticker_data.index = pd.to_datetime(ticker_data.index)

                self.ax.clear()
                self.vol_ax.clear()
                mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
                s = mpf.make_mpf_style(marketcolors=mc, gridcolor='gray', figcolor='#2e2e2e', y_on_right=True)
                # Only plot up to the current tick
                current_data_index = self.simulator.market.current_tick
                data_to_plot = ticker_data.iloc[:current_data_index]
                mpf.plot(data_to_plot, type='candle', ax=self.ax, volume=self.vol_ax, style=s, warn_too_much_data=1000)

                # Plot trades for the specific chart_ticker
                buy_trades = [trade for trade in self.simulator.portfolio.trades if trade['type'] == 'buy' and trade['symbol'] == chart_ticker]
                sell_trades = [trade for trade in self.simulator.portfolio.trades if trade['type'] == 'sell' and trade['symbol'] == chart_ticker]

                buy_dates = [trade['date'] for trade in buy_trades]
                buy_prices = [trade['price'] for trade in buy_trades]
                sell_dates = [trade['date'] for trade in sell_trades]
                sell_prices = [trade['price'] for trade in sell_trades]

                plotted_dates = data_to_plot.index.tolist()
                buy_x = [plotted_dates.index(d) for d in buy_dates if d in plotted_dates]
                sell_x = [plotted_dates.index(d) for d in sell_dates if d in plotted_dates]

                self.ax.plot(buy_x, buy_prices, '^', markersize=10, color='green', label='Buy', alpha=0.7)
                self.ax.plot(sell_x, sell_prices, 'v', markersize=10, color='red', label='Sell', alpha=0.7)

        self.equity_ax.clear()
        if self.simulator.portfolio_history:
            self.equity_ax.plot(self.simulator.portfolio_history, color='purple')
            self.equity_ax.set_title('Portfolio Equity Curve')
            self.equity_ax.set_xlabel('Time (Ticks)')
            self.equity_ax.set_ylabel('Portfolio Value')
            self.equity_ax.grid(True)

        self.canvas.draw()

        # Update portfolio values using get_current_prices
        current_prices = self.simulator.market.get_current_prices()
        if current_prices:
            total_value = self.simulator.portfolio.get_total_value(current_prices)
            cash = self.simulator.portfolio.cash
            holdings_text = "Holdings: "
            for symbol, quantity in self.simulator.portfolio.positions.items():
                price_for_holding = current_prices.get(symbol, 0)
                holding_value = quantity * price_for_holding
                holdings_text += f"{symbol}: {quantity} shares (₹{holding_value:,.2f}) "
            if not self.simulator.portfolio.positions:
                holdings_text += "None"
            self.portfolio_label.config(text=f"Portfolio Value: ₹{total_value:,.2f}   |   Cash: ₹{cash:,.2f}")
            self.holdings_label.config(text=holdings_text)
            if len(self.simulator.portfolio_history) > 1:
                analysis = Analysis(self.simulator.portfolio_history, benchmark_history=self.simulator.benchmark_history)
                total_return = analysis.get_total_return()
                cagr = analysis.get_cagr()
                sharpe_ratio = analysis.get_sharpe_ratio()
                sortino_ratio = analysis.get_sortino_ratio()
                max_drawdown = analysis.get_max_drawdown()
                calmar_ratio = analysis.get_calmar_ratio()
                alpha, beta = analysis.get_alpha_beta()
                var_95 = analysis.get_var(confidence_level=0.95)
                cvar_95 = analysis.get_cvar(confidence_level=0.95)

                self.metrics_label.config(text=f"Return: {total_return:.2%} | CAGR: {cagr:.2%} | Sharpe: {sharpe_ratio:.2f} | Sortino: {sortino_ratio:.2f} | Drawdown: {max_drawdown:.2%} | Calmar: {calmar_ratio:.2f} | Alpha: {alpha:.2f} | Beta: {beta:.2f}")
                self.var_label.config(text=f"VaR (95%): {var_95:.2%}")
                self.cvar_label.config(text=f"CVaR (95%): {cvar_95:.2%}")

        # Adjust update speed based on interval
        update_delay = 200 # Default for daily
        interval = self.interval_selection.get()
        if interval == '1m':
            update_delay = 50
        elif interval == '5m':
            update_delay = 100
        elif interval == '1h':
            update_delay = 150
        elif interval == '1d':
            update_delay = 200
        elif interval == '1wk':
            update_delay = 300
        elif interval == '1mo':
            update_delay = 500
        self.root.after(update_delay, self.update_chart)
