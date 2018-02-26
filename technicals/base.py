import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick2_ohlc
from bokeh.layouts import gridplot
from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead
from bokeh.plotting import figure, show, output_file
from bokeh.io import output_notebook
from bokeh.palettes import Colorblind as default_palette

class CoreData:
    def __init__(self, data):
        self.data = data
        self.data.rename({col:col.lower() for col in self.data.columns})
        self.columns = self.data.columns
        if not all(col in self.columns
                   for col in ['time', 'open', 'high', 'low', 'close']):
            print('ERROR: Not all required columns in the file')

class CoreAnalysis:
    def __init__(self, name, **parameters):
        pass

class TechnicalAnalysisCase(CoreData):
    def __init__(self, data):
        super().__init__(data)
        self.return_periods = []
        self.return_labels = {'trailing': [], 'forward': []}
        self.analyses = []
        self.indicator_columns = []

    def add_returns(self, periods):
        if all(isinstance(n, int) for n in periods):
            self.return_periods = self.return_periods + periods
        else:
            '''Raise Exception'''
            print('Windows must be a list of integers')
            return

        # Create trailing and forward returns for each period
        for period in periods:
            key1 = '-%dP_return' % period
            key2 = '+%dP_return' % period
            self.return_labels['trailing'].append(key1)
            self.return_labels['forward'].append(key2)
            self.data[key1] = \
                100*(self.data['close']/self.data['close'].shift(period))-100
            self.data[key2] = \
                100*(self.data['close'].shift(-1*period)/self.data['close'])-100

        return

    def add_SMA(self, periods):
        self.SMA_periods = periods
        self.SMA_labels = []
        for period in periods:
            sma_name = 'SMA' + str(period)
            self.SMA_labels.append(sma_name)
            self.data[sma_name] = \
                    self.data['close'].rolling(window=period).mean()
        if 'SMA' not in self.analyses:
            self.analyses.append('SMA')
        return

    def add_EMA(self, periods):
        self.EMA_periods = periods
        self.EMA_labels = []
        for period in periods:
            ema_name = 'EMA' + str(period)
            self.EMA_labels.append(ema_name)
            self.data[ema_name] = \
                    self.data['close'].ewm(span=period).mean()
        if 'EMA' not in self.analyses:
            self.analyses.append('EMA')
        return

    def add_MACrosses(self, cross_periods, kind='SMA'):
        if not any(analysis in self.analyses for analysis in ['SMA', 'EMA']):
            print('ERROR: Please add moving averages first')
            return

        if len(cross_periods) != 2:
            print('Error: Only two moving averages can be compared at a time')
            return

        if kind == 'SMA':
            all_periods = self.SMA_periods
        else:
            all_periods = self.EMA_periods
        if not all(period in all_periods for period in cross_periods):
            print('ERROR: Not all required columns in the file')
            return

        short_period = min(cross_periods)
        long_period = max(cross_periods)
        if kind == 'EMA':
            short_label = 'EMA' + str(short_period)
            long_label = 'EMA' + str(long_period)
            cross_label = 'EMA' + str(short_period) + '_'\
                                + str(long_period) + '_crosses'
            diff_label = 'EMA' + str(short_period) + '_'\
                               + str(long_period) + '_difference'
        elif kind == 'SMA':
            short_label = 'SMA' + str(short_period)
            long_label = 'SMA' + str(long_period)
            cross_label = 'SMA' + str(short_period) + '_' + str(long_period)
            cross_label = 'SMA' + str(short_period) + '_'\
                                + str(long_period) + '_crosses'
            diff_label = 'SMA' + str(short_period) + '_'\
                               + str(long_period) + '_difference'
        else:
            print("Kind must be 'SMA' or 'EMA'")
            return

        self.data[diff_label] = \
                        self.data[short_label] - self.data[long_label]
        self.data[cross_label] = 0
        for i in range(1, len(self.data)):
            diff_0 = self.data.loc[self.data.index[i-1], diff_label]
            diff_1 = self.data.loc[self.data.index[i], diff_label]
            if (diff_0 < 0) and (diff_1 > 0):    # when shorter > longer happens
                self.data.loc[self.data.index[i], cross_label] = 1
            elif (diff_0 > 0) and (diff_1 < 0):
                self.data.loc[self.data.index[i], cross_label] = -1

        self.analyses.append(kind+'MACrosses')
        self.indicator_columns.append(cross_label)
        return

    def add_BollingerBands(self, bollinger_period=20):
        if ('SMA' not in self.analyses) or \
                            (bollinger_period not in self.SMA_periods):
            self.add_SMA(periods=[bollinger_period])

        self.bollinger_period = bollinger_period
        sma_name = 'SMA' + str(bollinger_period)
        label_stem = 'Bollinger' + str(bollinger_period) + '_'
        self.data[label_stem + 'sigma'] = \
                    self.data['close'].rolling(window=bollinger_period).std()
        self.data[label_stem + 'upper_2sigma'] = \
                    self.data['close'] + 2*self.data[label_stem + 'sigma']
        self.data[label_stem + 'upper_3sigma'] = \
                    self.data['close'] + 3*self.data[label_stem + 'sigma']
        self.data[label_stem + 'lower_2sigma'] = \
                    self.data['close'] - 2*self.data[label_stem + 'sigma']
        self.data[label_stem + 'lower_3sigma'] = \
                    self.data['close'] - 3*self.data[label_stem + 'sigma']

        return

    def add_MACD(self, period_short=12, period_long=26, period_ave=9):
        if self.EMA_periods:
            ema_periods_to_add = [p
                                for p in [period_short, period_long, period_ave]
                                if p not in self.EMA_periods]
        else:
            ema_periods_to_add = [period_short, period_long, period_ave]
        if ema_periods_to_add != []:
            self.add_EMA(ema_periods_to_add)

        name_short = 'EMA' + str(period_short)
        name_long =  'EMA' + str(period_long)
        self.data.loc[:, 'MACD'] = self.data[name_short] - self.data[name_long]
        self.data.loc[:, 'MACD_signal'] = \
                                self.data['MACD'].ewm(span=period_ave).mean()
        self.data.loc[:, 'MACD_histogram'] = \
                                self.data['MACD'] - self.data['MACD_signal']

        self.data['MACD_cross'] = 0
        for i in range(1, len(self.data)):
            diff_0 = self.data.loc[self.data.index[i-1], 'MACD_histogram']
            diff_1 = self.data.loc[self.data.index[i], 'MACD_histogram']
            if (diff_0 < 0) and (diff_1 > 0):    # when shorter > longer happens
                self.data.loc[self.data.index[i], 'MACD_cross'] = 1
            elif (diff_0 > 0) and (diff_1 < 0):
                self.data.loc[self.data.index[i], 'MACD_cross'] = -1
        self.indicator_columns.append('MACD_cross')
        return













    def whatever(self):
        pass
