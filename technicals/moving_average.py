import numpy as np
import pandas as pd
import math
import itertools
import matplotlib.pyplot as plt
from bokeh.layouts import gridplot
from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead
from bokeh.plotting import figure, show, output_file
from bokeh.io import output_notebook
from bokeh.palettes import Colorblind as default_palette
from utility import create_default_panel

class MA:
    def __init__(self, series, period=20):
        '''
        series : pd.Series
            Time series to take average of
        period : int
            number of periods to average
        '''
        self.series_name = series.name
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
        label = 'SMA' + str(period)

        self.ma_name = label
        self.data[label] = \
                self.data[self.series_name].rolling(window=period).mean()

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
        '''
        ***Note that the index is reset to a numerical index and the column
        for the old index should be named 'time' ***
        '''
        self.series_name = series.name
        self.data = series.to_frame()
        self.data['numerical_index'] = [i for i in range(len(self.data))]
        self.periods = periods
        self.moving_average_labels = []
        self.moving_average_type = type_
        if type_ == 'exponential':
            self.MAmodel = EMA
        else:
            self.MAmodel = SMA
        for period in periods:
            ma = self.MAmodel(series, period=period)
            self.moving_average_labels.append(ma.ma_name)
            self.data[ma.ma_name] = ma.data[ma.ma_name]
        self.crosses_added = False

    def getCrosses(self):
        if len(self.periods) != 2:
            print('Error: Only two moving averages can be compared at a time')
            return
        short_period = min(self.periods)
        long_period = max(self.periods)
        if self.MAmodel == EMA:
            short_label = 'EMA' + str(short_period)
            long_label = 'EMA' + str(long_period)
        else:
            short_label = 'SMA' + str(short_period)
            long_label = 'SMA' + str(long_period)

        self.short_ma_label = short_label
        self.long_ma_label = long_label

        # Get difference between short and long moving acerages
        self.data['ma_difference'] = \
                        self.data[short_label] - self.data[long_label]
        self.data['cross'] = 0
        for i in range(1, len(self.data)):
            diff_0 = self.data.loc[self.data.index[i-1], 'ma_difference']
            diff_1 = self.data.loc[self.data.index[i], 'ma_difference']
            if (diff_0 < 0) and (diff_1 > 0):    # when shorter > longer happens
                self.data.loc[self.data.index[i], 'cross'] = 1
            elif (diff_0 > 0) and (diff_1 < 0):
                self.data.loc[self.data.index[i], 'cross'] = -1

        self.crosses_added = True
        return

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
        data_to_plot = [self.series_name] + self.moving_average_labels
        colors = default_palette[len(data_to_plot)]
        for i, data_name in enumerate(data_to_plot):
            d = self.data[data_name]
            p.line(self.data['numerical_index'], d,
                   legend=data_name, color=colors[i])

        output_notebook()
        show(p)

    def plotWithCrosses(self, p=None, title=None, plot_width=800):
        '''bokeh implementation'''
        if not self.crosses_added:
            self.getCrosses()

        if p is None:
            TOOLS = "pan,wheel_zoom,box_zoom,zoom_in,zoom_out,hover,reset,save"
            p = figure(title=title,
                       tools=TOOLS, plot_width=plot_width)
            p.grid.grid_line_alpha=0.3
            #p.xaxis.axis_label = 'Date'
            p.yaxis.axis_label = 'Price'
            p.xaxis.major_label_orientation = math.pi/4

        # This will be used to skip the gap by using numerical index
        x_replacement_dictionary = {
                            i : date.strftime('%Y-%m-%d %-H:%M')
                            for i, date in enumerate(self.data.index)}
        p.xaxis.major_label_overrides = x_replacement_dictionary

        # Plot the MAs
        data_to_plot = [self.series_name] + self.moving_average_labels
        colors = default_palette[len(data_to_plot)]
        for i, data_name in enumerate(data_to_plot):
            d = self.data[data_name]
            p.line(self.data['numerical_index'], d,
                   legend=data_name, color=colors[i])

        # Plot the arrows indicating crosses
        goldenX = (self.data['cross'] == 1)
        deathX = (self.data['cross'] == -1)
        for ind in self.data[goldenX].index:
            p.add_layout(
                Arrow(
                    end=NormalHead(size=10,
                            fill_color="yellowgreen",
                            line_color="yellowgreen"
                ),
                line_color="yellowgreen", line_width=2,
                x_start=self.data.loc[ind, 'numerical_index'].astype('float'),
                x_end=self.data.loc[ind, 'numerical_index'].astype('float'),
                y_start=self.data.loc[ind, self.long_ma_label] - 0.5,
                y_end=self.data.loc[ind, self.long_ma_label] - 0.2))

        for ind in self.data[deathX].index:
            p.add_layout(
                Arrow(
                    end=NormalHead(size=10,
                            fill_color="salmon",
                            line_color="salmon"
                ),
                line_color="salmon", line_width=2,
                x_start=self.data.loc[ind, 'numerical_index'].astype('float'),
                x_end=self.data.loc[ind, 'numerical_index'].astype('float'),
                y_start=self.data.loc[ind, self.long_ma_label] + 0.5,
                y_end=self.data.loc[ind, self.long_ma_label] + 0.2))

        output_notebook()
        show(p)
        return

    def plot1(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        data_to_plot = [self.series_name] + self.moving_average_labels
        self.data[data_to_plot].plot(ax=ax)
        # add code here for figure attributes

    def plotWithCrosses1(self, ax=None):
        '''
        matplotlib implementation
        '''
        if not self.crosses_added:
            self.getCrosses()
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        self.plot1(ax=ax)
        goldenX = (self.data['cross'] == 1)
        deathX = (self.data['cross'] == -1)
        for ind in self.data[goldenX].index:
            y = self.data.loc[ind, self.long_ma_label] - 0.6
            dx = 0
            dy = 0.3
            ax.arrow(ind, y, dx, dy, color='green',
                     head_width=0.05, head_length=0.2)

        for ind in self.data[deathX].index:
            y = self.data.loc[ind, self.short_ma_label] + 0.6
            dx = 0
            dy = -0.3
            ax.arrow(ind, y, dx, dy, color='red',
                     head_width=0.05, head_length=0.2,)

        return
