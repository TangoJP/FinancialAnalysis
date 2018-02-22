import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from moving_average import MA, EMA, MACollection
from bokeh.layouts import gridplot
from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead, Legend
from bokeh.plotting import figure, show, output_file
from bokeh.io import output_notebook, show
from bokeh.layouts import column
from bokeh.palettes import Colorblind as default_palette
from moving_average import MA, SMA, MACollection
from utility import create_default_panel, plot_candlestick

class MACD:
    def __init__(self, data, series_name='close',
                 period_short=12, period_long=26, period_ave=9):
        self.data = data
        self.series_name = series_name
        self.data.loc[:, 'numerical_index'] = [i for i in range(len(self.data))]

        ema_short = EMA(self.data[series_name], period=period_short)
        ema_long = EMA(self.data[series_name], period=period_long)
        name_short = ema_short.ma_name
        name_long = ema_long.ma_name
        self.data.loc[:, name_short] = ema_short.data[name_short]
        self.data.loc[:, name_long] = ema_long.data[name_long]
        self.data.loc[:, 'MACD'] = self.data[name_short] - self.data[name_long]
        signal = EMA(self.data['MACD'], period=period_ave)
        self.data.loc[:, 'MACD_signal'] = signal.data[signal.ma_name]
        self.data.loc[:, 'MACD_histogram'] = self.data['MACD'] - self.data['MACD_signal']

    def plot(self, title=None, plot_height=400, plot_width=800):
        '''
        Bokeh plot function that plots two panels, one for candlestick and the
        other for MACD indicators.
        '''
        p1 = create_default_panel(plot_height=plot_height,
                                  plot_width=plot_width)
        p1 = plot_candlestick(self.data, p=p1, show_plot=False,
                              plot_height=plot_height,
                              plot_width=plot_width)

        p2 = create_default_panel(plot_height=int(plot_width/4),
                                  plot_width=plot_width)
        p2.yaxis.axis_label = 'Price'
        w = plot_width / (10 * len(self.data))
        r0 = p2.vbar(x=self.data['numerical_index'], width=w,
               bottom=0, top=self.data['MACD_histogram'],
               fill_color=None, line_color="grey", line_alpha=0.3)
        r1 = p2.line(self.data['numerical_index'], self.data['MACD'],
               color='skyblue', line_width=1.2)
        r2 = p2.line(self.data['numerical_index'], self.data['MACD_signal'],
               color='salmon', line_width=1.2)
        legend = Legend(items=[
                            ("MACD", [r1]), ("Signal", [r2]), ("OSCI", [r0]),
                            ], location=(5, 0))

        p2.add_layout(legend, 'right')

        # This will skip the datetime gap by using numerical index
        x_replacement_dictionary = {
                            i : date.strftime('%Y-%m-%d %-H:%M')
                            for i, date in enumerate(self.data.index)}
        p1.xaxis.major_label_overrides = x_replacement_dictionary
        p2.xaxis.major_label_overrides = x_replacement_dictionary

        output_notebook()
        show(column(p1, p2))

    def getCrossSignals(self):
        self.data['cross'] = 0
        for i in range(1, len(self.data)):
            diff_0 = self.data.loc[self.data.index[i-1], 'MACD_histogram']
            diff_1 = self.data.loc[self.data.index[i], 'MACD_histogram']
            if (diff_0 < 0) and (diff_1 > 0):    # when shorter > longer happens
                self.data.loc[self.data.index[i], 'cross'] = 1
            elif (diff_0 > 0) and (diff_1 < 0):
                self.data.loc[self.data.index[i], 'cross'] = -1
