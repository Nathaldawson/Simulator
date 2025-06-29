
(https://github.com/user-attachments/assets/e2187158-6f0a-4649-9b51-fe7cc02edbb2)

 Simulator Project

This project simulates trading strategies on stock market data using Python. It includes a modular design with the following main components:

- **Market**: Handles market data loading and iteration.
- **Portfolio**: Manages cash, positions, and stop-loss logic.
- **Strategy**: Implements trading strategies (e.g., Moving Average, Buy and Hold, Momentum).
- **Simulator**: Orchestrates the simulation, connecting the market, portfolio, and strategy.
- **Visualizer**: (Optional) Provides a GUI for running and visualizing simulations.

## Requirements
- Python 3.7+
- pandas
- numpy
- tkinter (for GUI)

Install dependencies with:
```
pip install pandas numpy
```

## Usage
Run the simulator with the GUI:
```
python Simulator.py
```

## File Structure
- `Simulator.py`: Main simulation runner and entry point.
- `Market.py`: Market data handling.
- `Portfolio.py`: Portfolio management.
- `Strategy.py`: Trading strategies.
- `Visualizer.py`: GUI visualization (requires tkinter).

## Customization
- Add or modify strategies in `Strategy.py`.
- Change tickers, intervals, or simulation parameters in `Simulator.py` or via the GUI.

## License
MIT License.

---
Created by Nathal Dawson
