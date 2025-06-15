import backtrader as bt

class SuperTrend(bt.Indicator):
    """SuperTrend indicator implementation."""
    params = (('period', 7), ('multiplier', 3.0),)
    lines = ('supertrend',)
    plotinfo = dict(subplot=False)

    def __init__(self):
        self.atr = bt.indicators.ATR(self.data, period=self.p.period)
        self.upper_band = self.data.high + (self.p.multiplier * self.atr)
        self.lower_band = self.data.low - (self.p.multiplier * self.atr)
        self.uptrend = True
        super(SuperTrend, self).__init__()

    def next(self):
        if len(self.data) <= self.p.period:
            return

        if self.uptrend:
            if self.data.close[-1] < self.lines.supertrend[-1]:
                self.uptrend = False
                self.lines.supertrend[0] = self.upper_band[0]
            else:
                self.lines.supertrend[0] = max(self.lower_band[0], self.lines.supertrend[-1])
        else:
            if self.data.close[-1] > self.lines.supertrend[-1]:
                self.uptrend = True
                self.lines.supertrend[0] = self.lower_band[0]
            else:
                self.lines.supertrend[0] = min(self.upper_band[0], self.lines.supertrend[-1])

class OnBalanceVolume(bt.Indicator):
    """On Balance Volume (OBV) custom implementation."""
    lines = ('obv',)
    plotinfo = dict(subplot=True)

    def __init__(self):
        super(OnBalanceVolume, self).__init__()

    def next(self):
        if len(self) == 1:
            self.lines.obv[0] = 0
            return
        
        close_today = self.data.close[0]
        close_yesterday = self.data.close[-1]
        vol_today = self.data.volume[0]
        prev_obv = self.lines.obv[-1]

        if close_today > close_yesterday:
            self.lines.obv[0] = prev_obv + vol_today
        elif close_today < close_yesterday:
            self.lines.obv[0] = prev_obv - vol_today
        else:
            self.lines.obv[0] = prev_obv

class VolumeWeightedAveragePrice(bt.Indicator):
    """Custom Volume Weighted Average Price (VWAP) with daily reset."""
    lines = ('vwap',)
    plotinfo = dict(subplot=False)

    def __init__(self):
        # To reset VWAP daily, we need to track the date.
        self.addminperiod(1)
        self.tpv_cum = 0.0
        self.vol_cum = 0.0
        super(VolumeWeightedAveragePrice, self).__init__()

    def next(self):
        # Check if it's a new day to reset the cumulative values
        if len(self) > 1 and self.data.datetime.date(0) != self.data.datetime.date(-1):
            self.tpv_cum = 0.0
            self.vol_cum = 0.0

        typical_price = (self.data.high[0] + self.data.low[0] + self.data.close[0]) / 3
        volume = self.data.volume[0]

        self.tpv_cum += typical_price * volume
        self.vol_cum += volume

        if self.vol_cum > 0:
            self.lines.vwap[0] = self.tpv_cum / self.vol_cum
        else:
            # Fallback to close if no volume (e.g., first bar)
            self.lines.vwap[0] = self.data.close[0]