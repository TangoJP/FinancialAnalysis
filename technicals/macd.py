import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bokeh
import math
from moving_average import MA, EMA, MACollection

class MACD:
    def __init__(self, series, period_short=12, period_long=26, period_ave=9):
        series_name = series.name
        self.series_name = series_name
        self.data = series.to_frame()
        ema_short = EMA(series, period=period_short)
        ema_long = EMA(series, period=period_long)
        name_short = ema_short.ma_name
        name_long = ema_long.ma_name
        self.data[name_short] = ema_short.data[name_short]
        self.data[name_long] = ema_long.data[name_long]
        self.data['MACD'] = self.data[name_short] - self.data[name_long]
        signal = EMA(self.data['MACD'], period=period_ave)
        self.data['MACD_signal'] = signal.data[signal.ma_name]
        self.data['MACD_histogram'] = self.data['MACD'] - self.data['MACD_signal']
