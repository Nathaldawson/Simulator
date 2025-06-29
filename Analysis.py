import numpy as np
import pandas as pd
from scipy.stats import linregress

class Analysis:
    def __init__(self, portfolio_history, risk_free_rate=0.0, benchmark_history=None):
        self.portfolio_history = np.array(portfolio_history)
        self.risk_free_rate = risk_free_rate
        self.returns = self.calculate_returns()
        
        self.benchmark_history = None
        self.benchmark_returns = None
        if benchmark_history is not None:
            self.benchmark_history = np.array(benchmark_history)
            self.benchmark_returns = self.calculate_returns(self.benchmark_history)

    def calculate_returns(self, history=None):
        """
        Calculates the periodic returns of the portfolio or a given history.
        """
        if history is None:
            history = self.portfolio_history
        return (history[1:] - history[:-1]) / history[:-1]

    def get_total_return(self):
        """
        Calculates the total return of the strategy.
        """
        if len(self.portfolio_history) < 2:
            return 0.0
        return (self.portfolio_history[-1] / self.portfolio_history[0]) - 1

    def get_cagr(self, periods_per_year=252):
        """
        Calculates the Compound Annual Growth Rate (CAGR).
        """
        if len(self.portfolio_history) < 2:
            return 0.0
        total_return = self.get_total_return()
        num_periods = len(self.portfolio_history) - 1
        if num_periods == 0:
            return 0.0
        return (1 + total_return)**(periods_per_year / num_periods) - 1

    def get_sharpe_ratio(self, periods_per_year=252):
        """
        Calculates the Sharpe Ratio.
        """
        if len(self.returns) == 0:
            return 0.0
        excess_returns = self.returns - self.risk_free_rate / periods_per_year
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(periods_per_year)

    def get_sortino_ratio(self, periods_per_year=252):
        """
        Calculates the Sortino Ratio using downside deviation (standard deviation of negative returns only).
        """
        if len(self.returns) == 0:
            return 0.0
        target = self.risk_free_rate / periods_per_year
        downside_returns = np.where(self.returns < target, self.returns - target, 0)
        downside_deviation = np.sqrt(np.mean(downside_returns ** 2))
        if downside_deviation == 0:
            return np.inf
        excess_return = np.mean(self.returns - target)
        return excess_return / downside_deviation * np.sqrt(periods_per_year)

    def get_max_drawdown(self):
        """
        Calculates the maximum drawdown (largest peak-to-trough decline).
        """
        if len(self.portfolio_history) < 2:
            return 0.0
        values = np.array(self.portfolio_history)
        peaks = np.maximum.accumulate(values)
        drawdowns = (values - peaks) / peaks
        return np.min(drawdowns)

    def get_calmar_ratio(self, periods_per_year=252):
        """
        Calculates the Calmar Ratio.
        """
        max_drawdown = self.get_max_drawdown()
        if max_drawdown == 0:
            return np.inf
        cagr = self.get_cagr(periods_per_year)
        return cagr / abs(max_drawdown)

    def get_alpha_beta(self, periods_per_year=252):
        """
        Calculates Alpha and Beta relative to a benchmark.
        """
        if self.benchmark_returns is None or len(self.returns) < 2 or len(self.benchmark_returns) < 2:
            return 0.0, 0.0 # Cannot calculate without sufficient data

        # Ensure returns are of the same length
        min_len = min(len(self.returns), len(self.benchmark_returns))
        portfolio_returns_aligned = self.returns[-min_len:]
        benchmark_returns_aligned = self.benchmark_returns[-min_len:]

        # Add risk-free rate to benchmark returns for regression
        benchmark_excess_returns = benchmark_returns_aligned - self.risk_free_rate / periods_per_year
        portfolio_excess_returns = portfolio_returns_aligned - self.risk_free_rate / periods_per_year

        # Perform linear regression
        beta, alpha_daily, r_value, p_value, std_err = linregress(benchmark_excess_returns, portfolio_excess_returns)
        
        # Annualize alpha
        alpha = alpha_daily * periods_per_year
        
        return alpha, beta

    def print_report(self):
        """
        Prints a summary of the performance metrics.
        """
        print("\n--- Performance Analysis ---")
        print(f"Total Return: {self.get_total_return():.2%}")
        print(f"CAGR: {self.get_cagr():.2%}")
        print(f"Sharpe Ratio: {self.get_sharpe_ratio():.2f}")
        print(f"Sortino Ratio: {self.get_sortino_ratio():.2f}")
        print(f"Maximum Drawdown: {self.get_max_drawdown():.2%}")
        print(f"Calmar Ratio: {self.get_calmar_ratio():.2f}")
        
        if self.benchmark_history is not None:
            alpha, beta = self.get_alpha_beta()
            print(f"Alpha: {alpha:.2f}")
            print(f"Beta: {beta:.2f}")

    def get_var(self, confidence_level=0.95):
        """
        Calculates Value at Risk (VaR) at a given confidence level.
        Assumes returns are sorted for percentile calculation.
        """
        if len(self.returns) == 0:
            return 0.0
        sorted_returns = np.sort(self.returns)
        # VaR is the loss at the given confidence level
        var_index = int(np.floor((1 - confidence_level) * len(sorted_returns)))
        return sorted_returns[var_index]

    def get_cvar(self, confidence_level=0.95):
        """
        Calculates Conditional Value at Risk (CVaR) at a given confidence level.
        Also known as Expected Shortfall.
        """
        if len(self.returns) == 0:
            return 0.0
        sorted_returns = np.sort(self.returns)
        # Find all returns that are worse than VaR
        var_index = int(np.floor((1 - confidence_level) * len(sorted_returns)))
        cvar_returns = sorted_returns[:var_index+1]
        if len(cvar_returns) == 0:
            return 0.0
        return np.mean(cvar_returns)

    def print_report(self):
        """
        Prints a summary of the performance metrics.
        """
        print("\n--- Performance Analysis ---")
        print(f"Total Return: {self.get_total_return():.2%}")
        print(f"CAGR: {self.get_cagr():.2%}")
        print(f"Sharpe Ratio: {self.get_sharpe_ratio():.2f}")
        print(f"Sortino Ratio: {self.get_sortino_ratio():.2f}")
        print(f"Maximum Drawdown: {self.get_max_drawdown():.2%}")
        print(f"Calmar Ratio: {self.get_calmar_ratio():.2f}")
        print(f"Value at Risk (95%): {self.get_var(0.95):.2%}")
        print(f"Conditional VaR (95%): {self.get_cvar(0.95):.2%}")
        
        if self.benchmark_history is not None:
            alpha, beta = self.get_alpha_beta()
            print(f"Alpha: {alpha:.2f}")
            print(f"Beta: {beta:.2f}")
