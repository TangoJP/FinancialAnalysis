import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bokeh
import math
from moving_average import MA, SMA, MACollection

class BollingerBand:
    def __init__(self, series, period=20):
        sma = SMA(series, period=period)
        self.data = sma.data
        self.series_name = sma.series_name
        self.ma_name = sma.ma_name
        self.period = period
        
        self.data['sigma'] = \
                        self.data[self.series_name].rolling(window=period).std()
        self.data['upper_2sigma'] = \
                        self.data[self.ma_name] + 2 * self.data['sigma']
        self.data['upper_3sigma'] = \
                        self.data[self.ma_name] + 3 * self.data['sigma']
        self.data['lower_2sigma'] = \
                        self.data[self.ma_name] - 2 * self.data['sigma']
        self.data['lower_3sigma'] = \
                        self.data[self.ma_name] - 3 * self.data['sigma']

    def plot(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        self.data[[self.series_name, self.ma_name]].plot(ax=ax),
        self.data[['upper_2sigma', 'lower_2sigma']].plot(ax=ax, ls=':')
        self.data[['upper_3sigma', 'lower_3sigma']].plot(ax=ax, ls='--')
