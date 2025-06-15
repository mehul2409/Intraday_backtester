import os
import backtrader as bt
import polars as pl
from .report_generator import generate_html_report
from .config import INDICATORS

class PolarsDataFeed(bt.feeds.PandasData):
    """
    A custom Backtrader data feed that accepts a Polars DataFrame.
    This version is more robust to handle different initialization patterns.
    """
    def __init__(self, *args, **kwargs):
        # The data can be passed as a positional arg or a keyword arg 'dataname'
        dataname = kwargs.get('dataname', None)
        if not dataname and args:
            dataname = args[0]
        
        if isinstance(dataname, pl.DataFrame):
            # Convert Polars to Pandas for Backtrader
            pd_df = dataname.to_pandas(use_pyarrow_extension_array=True)
            pd_df.set_index('datetime', inplace=True)
            kwargs['dataname'] = pd_df # Set the keyword arg for the parent class
            
            # If 'dataname' was a positional arg, remove it from args
            if args and args[0] is dataname:
                args = args[1:]

        super(PolarsDataFeed, self).__init__(*args, **kwargs)

class DualIndicatorStrategy(bt.Strategy):
    params = (
        ('indicator1_name', None), ('indicator2_name', None),
        ('indicator1_params', {}), ('indicator2_params', {}),
    )

    def __init__(self):
        indicator1_class = INDICATORS[self.p.indicator1_name]
        indicator2_class = INDICATORS[self.p.indicator2_name]
        
        # CORRECTED: Initialize indicators using the explicit self.datas[0]
        # This is more robust than using the self.data alias.
        self.ind1 = indicator1_class(self.datas[0], **self.p.indicator1_params)
        self.ind2 = indicator2_class(self.datas[0], **self.p.indicator2_params)
        self.order = None

    def _get_signal(self, indicator_name, indicator):
        # This logic determines buy/sell signals based on common indicator behavior
        try:
            if indicator_name == 'RSI':
                if indicator.lines.rsi[0] < 30: return 1
                if indicator.lines.rsi[0] > 70: return -1
            elif indicator_name == 'Stochastic':
                if indicator.lines.percK[0] < 20: return 1
                if indicator.lines.percK[0] > 80: return -1
            elif indicator_name == 'MACD':
                if indicator.lines.macd[0] > indicator.lines.signal[0]: return 1
                if indicator.lines.macd[0] < indicator.lines.signal[0]: return -1
            elif indicator_name == 'CCI':
                if indicator.lines.cci[0] < -100: return 1
                if indicator.lines.cci[0] > 100: return -1
            elif indicator_name == 'WilliamsR':
                if indicator.lines.percR[0] < -80: return 1
                if indicator.lines.percR[0] > -20: return -1
            elif indicator_name == 'Supertrend':
                if self.data.close[0] > indicator.lines.supertrend[0]: return 1
                if self.data.close[0] < indicator.lines.supertrend[0]: return -1
            elif indicator_name == 'VWAP':
                if self.data.close[0] > indicator.lines.vwap[0]: return 1
                if self.data.close[0] < indicator.lines.vwap[0]: return -1
            else: # Fallback for simple single-line indicators
                if self.data.close[0] > indicator.lines[0][0]: return 1
                if self.data.close[0] < indicator.lines[0][0]: return -1
        except IndexError:
            # Not enough data to compute indicator yet
            return 0
        return 0

    def next(self):
        if self.order: return
        signal1 = self._get_signal(self.p.indicator1_name, self.ind1)
        signal2 = self._get_signal(self.p.indicator2_name, self.ind2)
        if not self.position:
            if signal1 == 1 and signal2 == 1: self.order = self.buy()
        else:
            if signal1 == -1 or signal2 == -1: self.order = self.sell()
    
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            self.order = None

def run_single_backtest(args):
    company, (ind1_name, ind2_name), params1, params2 = args
    try:
        data_path = f'data/processed/{company}.parquet'
        if not os.path.exists(data_path): return f"SKIPPED: Data for {company} not found."
        data = pl.read_parquet(data_path)
        if data.is_empty(): return f"SKIPPED: Data for {company} is empty."
    except Exception as e:
        return f"ERROR loading data for {company}: {e}"
    try:
        cerebro = bt.Cerebro(stdstats=False)
        cerebro.adddata(PolarsDataFeed(dataname=data))
        cerebro.addstrategy(
            DualIndicatorStrategy,
            indicator1_name=ind1_name, indicator2_name=ind2_name,
            indicator1_params=params1, indicator2_params=params2,
        )
        cerebro.broker.set_cash(100000.0)
        cerebro.broker.setcommission(commission=0.002)
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio', timeframe=bt.TimeFrame.Days, compression=1, riskfreerate=0.0, annualize=True)
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        results = cerebro.run()
        final_portfolio_value = cerebro.broker.getvalue()
        trade_analysis = results[0].analyzers.trade_analyzer.get_analysis()
        sharpe_ratio = results[0].analyzers.sharpe_ratio.get_analysis().get('sharperatio', None)
        max_drawdown = results[0].analyzers.drawdown.get_analysis().max.drawdown
        generate_html_report(
            company=company, ind1_name=ind1_name, ind2_name=ind2_name,
            params1=params1, params2=params2, final_value=final_portfolio_value,
            pnl=final_portfolio_value - 100000.0, trades=trade_analysis,
            sharpe=sharpe_ratio, max_dd=max_drawdown
        )
        return f"Completed: {company} {ind1_name}/{ind2_name} with PNL: {final_portfolio_value - 100000.0:.2f}"
    except Exception as e:
        return f"ERROR during backtest for {company} with {ind1_name}/{ind2_name}: {e}"
