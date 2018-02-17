import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from moving_average import MA, EMA, MACollection
from bokeh.layouts import gridplot
from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead
from bokeh.plotting import figure, show, output_file
from bokeh.io import output_notebook
from bokeh.palettes import Colorblind as default_palette
from moving_average import MA, SMA, MACollection
from utility import create_default_panel

class MACD:
    def __init__(self, series, period_short=12, period_long=26, period_ave=9):
        series_name = series.name
        self.series_name = series_name
        self.data = series.to_frame()
        self.data['numerical_index'] = [i for i in range(len(self.data))]

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

    def plot(self, p=None, title=None, plot_width=800):
        if p is None:
            p = create_default_panel(plot_width=plot_width)
        p.yaxis.axis_label = 'Price'
        w = plot_width / (10 * len(self.data))

        # This will be used to skip the datetime gap by using numerical index
        x_replacement_dictionary = {
                            i : date.strftime('%Y-%m-%d %-H:%M')
                            for i, date in enumerate(self.data.index)}
        p.xaxis.major_label_overrides = x_replacement_dictionary

        p.vbar(x=self.data['numerical_index'], width=w,
               bottom=0, top=self.data['MACD_histogram'],
               fill_color=None, line_color="grey", line_alpha=0.3)
        p.line(self.data['numerical_index'], self.data['MACD'],
               legend='MACD', color='skyblue', line_width=1.2)
        p.line(self.data['numerical_index'], self.data['MACD_signal'],
               legend='MACD_signal', color='salmon', line_width=1.2)

        output_notebook()
        show(p)
