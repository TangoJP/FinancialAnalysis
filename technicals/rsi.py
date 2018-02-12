import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bokeh
import math
from moving_average import MA, SMA, EMA, MACollection

def calculate_RSI(RS):
    RSI = 100 - (100 / (1 + RS))
    return RSI

class RSI:
    def __init__(self, series, period=14):
        self.series_name = series.name
        self.data = series.to_frame()
        self.period = period

        self.data['change'] = \
            self.data[self.series_name] - self.data[self.series_name].shift(1)
        self.data['ave_gain'] = 0
        self.data['ave_loss'] = 0

        counter = period - 1
        first_subset = self.data.iloc[:period]
        inc = first_subset['change'] >= 0
        dec = first_subset['change'] < 0
        ind = self.data.index[counter]
        self.data.loc[ind, 'ave_gain'] = \
                            first_subset['change'][inc].sum() / period
        self.data.loc[ind, 'ave_loss'] = \
                            (-1)*first_subset['change'][dec].sum() / period
        counter += 1

        while counter < len(self.data):
            subset = self.data.iloc[(counter-period + 1):counter+1]
            ind = self.data.index[counter]

            if self.data.iloc[counter]['change'] >=0:
                current_gain = self.data.iloc[counter]['change']
                current_loss = 0
            else:
                current_gain = 0
                current_loss = (-1)*self.data.iloc[counter]['change']
            previous_ave_gain = self.data.iloc[counter-1]['ave_gain']
            previous_ave_loss = self.data.iloc[counter-1]['ave_loss']

            self.data.loc[ind, 'ave_gain'] = \
                (previous_ave_gain * (period -1) + current_gain) / period
            self.data.loc[ind, 'ave_loss'] = \
                (previous_ave_loss * (period -1) + current_loss) / period

            counter += 1

        self.data['RS'] = self.data['ave_gain'] / self.data['ave_loss']
        self.data['RSI']  = self.data['RS'].apply(calculate_RSI)

    def plot(self):
        fig1, ax1 = plt.subplots(1, 1, figsize=(16, 6))
        fig2, ax2 = plt.subplots(1, 1, figsize=(16, 3))
        self.data[self.series_name].plot(ax=ax1),
        self.data['RSI'].plot(ax=ax2, color='salmon')
        ax2.axhline(y=50, ls=':', color='0.8')
