# this class implements various analyses for a company stcok

import os
import scipy.stats as scs
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt

class AbstractStock:
    pass

class Stock:
    ''' It takes in a company's name (or ticker) and retrieves the market data
    into pandas table. Methods will be used for various analyses of the
    stock performance
    '''

    def __init__(self, comp_name, start=None, end=None):
        ''' Retrieves the 'comp_name' stock information into pandas table.

        source : string
            infomration source : 'yahoo', 'goog', or ???
        start : string
             start date for the retrieved info. YYYY-MM-DD format
        end: string
            end date for the retrieved info. YYYY-MM-DD format

        *** Currently only supports 'yahoo' as source
        '''
        if (isinstance(comp_name, str)) and ('.csv' in comp_name):
            data = pd.read_csv(comp_name)
            data['Date'] = pd.to_datetime(data['Date'])
            data_table = data.set_index('Date')
            data_table = data_table.replace('null', np.NaN)
            #data_table = data_table.dropna()
            self.data_table = data_table.astype('float')
            ticker = os.path.split(comp_name)[1]
            self.ticker = ticker.replace('.csv', '')
        else:
            self.ticker = comp_name
            self.data_table = web.DataReader(name=self.ticker,
                                             data_source='yahoo',
                                             start=start,
                                             end=end)
        self.start_date = self.data_table.index.min()
        self.end_date = self.data_table.index.max()

    #  PLOTTING SIMPLE DATA
    # plot historical price info
    def simple_price_plot(self, ax=None, reset_zero=False):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        if reset_zero:
            data = self.data_table['Close'] / self.data_table['Close'].iloc[0]
        else:
            data = self.data_table['Close']
        ax.plot(self.data_table.index.date, data, label=self.ticker)
        ax.legend()

    # plot historical volume info
    def simple_vol_plot(self, width=0.01, ax=None):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        ax.bar(self.data_table.index.date, self.data_table['Volume'], width=width)
        ax.set_ylabel('Volume (Shares)')

    # METHODS FOR MOVING AVERAGES
    def getSMA(self, window=20):
        return self.data_table['Close'].rolling(window=window).mean()

    def getSMVar(self, window=20):
        return self.data_table['Close'].rolling(window=window).var()

    def getSMStd(self, window=20):
        return self.data_table['Close'].rolling(window=window).std()

    def plotSMA(self, window=20, ax=None, color='salmon'):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        ax.plot(self.data_table.index.date, self.data_table['Close'])
        ax.plot(self.data_table.index.date, self.getSMA(window=window), color=color)
        ax.set_ylabel('%s SMA ($)' % self.ticker)

    def plotSMVar(self, window=20, ax=None, color='salmon'):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        ax.plot(self.data_table.index.date, self.getSMVar(window=window), color=color)
        ax.set_ylabel('%s SMVar' % self.ticker)

    def plotSMStd(self, window=20, ax=None, color='salmon'):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        ax.plot(self.data_table.index.date, self.getSMStd(window=window), color=color)
        ax.set_ylabel('%s SMStd' % self.ticker)

    def getEMA(self, span=20):
        return self.data_table['Close'].ewm(span=span).mean()

    def getEMVar(self, span=20):
        return self.data_table['Close'].ewm(span=span).var()

    def getEMStd(self, span=20):
        return self.data_table['Close'].ewm(span=span).std()

    def plotEMA(self, span=20, ax=None, color='salmon'):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        ax.plot(self.data_table.index.date, self.data_table['Close'])
        ax.plot(self.data_table.index.date, self.getEMA(span=span), color=color)
        ax.set_ylabel('%s EMA ($)' % self.ticker)

    def plotEMVar(self, span=20, ax=None, color='salmon'):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        ax.plot(self.data_table.index.date, self.getEMVar(span=span), color=color)
        ax.set_ylabel('%s EMVar' % self.ticker)

    def plotEMStd(self, span=20, ax=None, color='salmon'):
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 3))
        ax.plot(self.data_table.index.date, self.getEMStd(span=span), color=color)
        ax.set_ylabel('%s EMStd' % self.ticker)

    # METHODS FOR STOCK PRICCE STATS
    # calculates daily return with linear, log scale, or percentage change

    #def return_var(self, scale='log'):
    #    if scale == 'linear':
    #        return np.nanvar(self.data_table['linear_return'])
    #    elif scale == 'log':
    #        return np.nanvar(self.data_table['log_return'])
    #    else:
    #        print("ERROR: Scale must be set to 'linear' or 'log'")

    #def return_std(self, scale='log'):
    #    if scale == 'linear':
    #        return np.nanstd(self.data_table['linear_return'])
    #    elif scale == 'log':
    #        return np.nanstd(self.data_table['log_return'])
    #    else:
    #        print("ERROR: Scale must be set to 'linear' or 'log'")

    #def daily_return_hist(self, scale='log', bins=50, ax=None):
    #    if ax is None:
    #        fig, ax = plt.subplots(1, 1, figsize=(6, 3))
    #    if scale == 'linear':
    #        ax.hist(self.data_table['linear_return'].dropna(), bins=bins)
    #        ax.set_xlabel('Daily Linear Return on %s' % self.ticker)
    #        ax.set_ylabel('Frequency in number of days')
    #    elif scale == 'log':
    #        ax.hist(self.data_table['log_return'].dropna(), bins=bins)
    #        ax.set_xlabel('Daily Log Return on %s' % self.ticker)
    #        ax.set_ylabel('Frequency in number of days')
    #    elif scale == 'percentage':
    #        ax.hist(self.data_table['linear_return'].dropna(), bins=bins)
    #        ax.set_xlabel('Daily Percentage Change of %s' % self.ticker)
    #        ax.set_ylabel('Frequency in number of days')
    #    else:
    #        print("ERROR: Scale must be set to 'linear', 'log', or 'percentage'")
