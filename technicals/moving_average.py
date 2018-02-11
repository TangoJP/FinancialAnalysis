import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bokeh
import math

class MA:
    def __init__(self, series, period=20):
        '''
        series : pd.Series
            Time series to take average of
        period : int
            number of periods to average
        '''
        series_name = series.name
        self.series_name = series_name
        self.data = series.to_frame()

    def plot(self, ax=None, color1='skyblue', color2='salmon'):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        ax.plot(self.data.index.date, self.data[self.series_name], color=color1)
        ax.plot(self.data.index.date, self.data[self.ma_name], color=color2)
        ax.set_ylabel('%s SMA' % self.ma_name)

class SMA(MA):
    '''
    Simple moving average.
    '''
    def __init__(self, series, period=20):
        super().__init__(series=series, period=period)
        series_name = series.name
        label = 'SMA' + str(period)

        self.ma_name = label
        self.data[label] = \
                self.data[series_name].rolling(window=period).mean()

    def plot(self, ax=None, color1='skyblue', color2='salmon'):
        super().plot(ax=ax, color1=color1, color2=color2)

class EMA(MA):
    '''
    Exponential moving average
    '''
    def __init__(self, series, period):
        super().__init__(series=series, period=period)
        series_name = series.name
        label = 'EMA' + str(period)

        self.ma_name = label
        self.data[label] = \
                self.data[series_name].ewm(span=period).mean()

    def plot(self, ax=None, color1='skyblue', color2='salmon'):
        super().plot(ax=ax, color1=color1, color2=color2)

class MACollection:
    def __init__(self, series, type_='simple', periods=[9, 20]):
        self.periods = periods
        self.moving_averages = []
        self.moving_average_type = type_
        if type_ == 'exponential':
            self.MAmodel = EMA
        else:
            self.MAmodel = SMA
        for period in periods:
            self.moving_averages.append(self.MAmodel(series, period=period))

    def plot(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        for ma in self.moving_averages:
            ma.plot(ax=ax)
        # add code here for figure attributes
