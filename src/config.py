import backtrader as bt
from itertools import product
from .custom_indicators import SuperTrend, OnBalanceVolume, VolumeWeightedAveragePrice

# --- Dictionary mapping string names to Backtrader indicator classes ---
INDICATORS = {
    # Trend
    'EMA': bt.indicators.ExponentialMovingAverage,
    'MACD': bt.indicators.MACD,
    'ADX': bt.indicators.AverageDirectionalMovementIndex,
    'Supertrend': SuperTrend,
    # Momentum
    'RSI': bt.indicators.RelativeStrengthIndex,
    'Stochastic': bt.indicators.Stochastic,
    'CCI': bt.indicators.CommodityChannelIndex,
    'WilliamsR': bt.indicators.WilliamsR,
    # Volatility
    'BollingerBands': bt.indicators.BollingerBands,
    'ATR': bt.indicators.AverageTrueRange,
    # Volume
    'OnBalanceVolume': OnBalanceVolume,
    'VWAP': VolumeWeightedAveragePrice,
    # Other
    'Ichimoku': bt.indicators.Ichimoku,
    'FibonacciPivotPoint': bt.indicators.FibonacciPivotPoint,
    'PivotPoint': bt.indicators.PivotPoint,
}

# --- Parameter Grids for each indicator you want to test ---
PARAM_GRID = {
    'EMA': {'period': [20, 50, 200]},
    'MACD': {'period_me1': [12], 'period_me2': [26], 'period_signal': [9]},
    'ADX': {'period': [14, 20]},
    'Supertrend': {'period': [7, 14], 'multiplier': [2.0, 3.0]},
    'RSI': {'period': [14, 21]},
    'Stochastic': {'period': [14], 'period_d': [3], 'period_k': [3]},
    'CCI': {'period': [14, 20, 30]},
    'WilliamsR': {'period': [14, 28]},
    'BollingerBands': {'period': [20, 30], 'devfactor': [2.0, 2.5]},
    'ATR': {'period': [14, 20]},
    'Ichimoku': {'tenkan': [9], 'kijun': [26], 'senkou': [52]},
    'OnBalanceVolume': {},
    'VWAP': {},
    'FibonacciPivotPoint': {},
    'PivotPoint': {},
}

def get_param_combinations(indicator_name):
    """
    CORRECTED: This function is now a proper generator, always yielding
    dictionaries, which prevents type errors downstream.
    """
    # If indicator has no params in the grid, yield a single empty dictionary.
    if indicator_name not in PARAM_GRID or not PARAM_GRID[indicator_name]:
        yield {}
        return  # Stop the generator explicitly.

    param_names = list(PARAM_GRID[indicator_name].keys())
    param_values = list(PARAM_GRID[indicator_name].values())

    # Create all combinations of parameter values.
    for instance in product(*param_values):
        yield dict(zip(param_names, instance))
