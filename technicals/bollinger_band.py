import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from bokeh.layouts import gridplot
from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead
from bokeh.plotting import figure, show, output_file
from bokeh.io import output_notebook
from bokeh.palettes import Colorblind as default_palette
from moving_average import MA, SMA, MACollection
from utility import create_default_panel

class BollingerBand:
    def __init__(self, series, period=20):
        sma = SMA(series, period=period)
        self.data = sma.data
        self.data['numerical_index'] = [i for i in range(len(self.data))]
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

    def plot(self, p=None, title=None, plot_width=800):
        if p is None:
            p = create_default_panel(title=title, plot_width=plot_width)
        p.yaxis.axis_label = 'Price'

        # This will be used to skip the datetime gap by using numerical index
        x_replacement_dictionary = {
                            i : date.strftime('%Y-%m-%d %-H:%M')
                            for i, date in enumerate(self.data.index)}
        p.xaxis.major_label_overrides = x_replacement_dictionary

        # Plot each
        p.line(self.data['numerical_index'], self.data[self.series_name],
               legend=self.series_name, color='black', line_width=0.5)
        p.line(self.data['numerical_index'], self.data[self.ma_name],
               legend=self.ma_name, color='skyblue')
        p.line(self.data['numerical_index'], self.data['upper_2sigma'],
               legend='upper_2sigma', color='orange', line_dash='dashed')
        p.line(self.data['numerical_index'], self.data['lower_2sigma'],
               legend='lower_2sigma', color='orange', line_dash='dashed')
        p.line(self.data['numerical_index'], self.data['upper_3sigma'],
               legend='upper_3sigma', color='salmon', line_dash='dotted')
        p.line(self.data['numerical_index'], self.data['lower_3sigma'],
               legend='lower_3sigma', color='salmon', line_dash='dotted')

        output_notebook()
        show(p)

    def plot1(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        self.data[[self.series_name, self.ma_name]].plot(ax=ax),
        self.data[['upper_2sigma', 'lower_2sigma']].plot(ax=ax, ls=':')
        self.data[['upper_3sigma', 'lower_3sigma']].plot(ax=ax, ls='--')
