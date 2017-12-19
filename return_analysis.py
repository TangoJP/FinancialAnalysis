import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from stock import Stock
from base_analysis import BaseAnalysis

class ReturnAnalysis(BaseAnalysis):
    def __init__(self, stock, start=None, end=None, return_type='log',
                 future=False, windows=[1, 10, 20, 50, 100, 200]):
        super().__init__(stock, start=start, end=end)
        '''
        return_type : str
            If 'linear', linear return will be used. Otherwise, it's set
            to log return.
        future : Boolean
            If future=True, the return columns indicate the X-day returns from
            that day in the future. If False, they indicate X-day returns up to
            that day.
        windows : int list/array
            A list of X-day windows to be used for the return analysis
        '''
        self.return_type = return_type

        # Initialize windows
        if all(isinstance(n, int) for n in windows):
            self.windows = windows
        else:
            '''Raise Exception'''
            print('Windows must be a list of integers')
            return

        # Create returns for each window
        window_labels = []
        if future:
            for window in windows:
                key = '%dday_return' % window
                window_labels.append(key)
                if self.return_type == 'linear':
                    self.data['daily_return'] = \
                        (self.data['Close'].shift(-1*window)/self.data['Close'])-1
                else:
                    self.data[key] = \
                        np.log(self.data['Close'].shift(-1*window)/self.data['Close'])
        else:
            for window in windows:
                key = '%dday_return' % window
                window_labels.append(key)
                if self.return_type == 'linear':
                    self.data['daily_return'] = \
                        (self.data['Close']/self.data['Close'].shift(window))-1
                else:
                    self.data[key] = \
                        np.log(self.data['Close']/self.data['Close'].shift(window))
        self._window_labels = window_labels

    def print_info(self):
        n_points = len(self.data['Close'])
        n_na = np.sum(self.data['Close'].isnull())

        print('=='*6, '%s Basic Info' % self.ticker, '=='*6)
        print('Start Date - %s' % self.start_date.strftime("%Y-%m-%d"))
        print(' End  Date - %s' % self.end_date.strftime("%Y-%m-%d"))
        print('Number of data points - %d' % n_points)
        print('Number of missing data points - %d' % n_na)

    def plot(self, figsize=(18, 4)):
        '''
        Plot returns against time.
        '''
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        self.data[self._window_labels].plot(ax=ax, alpha=0.5)
        return

    def hist(self, bins=50, figsize=(18, 4)):
        '''
        Histogram of the returns.
        '''
        fig = plt.figure(figsize=figsize)
        num_plots = len(self._window_labels)

        # Plot X-day returns
        for i, w in enumerate(self.windows):
            key = '%dday_return' % w
            df = self.data[key]

            ax = fig.add_subplot(1, num_plots, i+1)
            sns.distplot(self.data[key].dropna(), ax=ax)
            ax.set_xlabel(key)

        plt.tight_layout()

        return

    def violinplot(self, bw=0.2, cut=1, figsize=(8, 6)):
        '''
        violinplot of the returns.
        '''
        fig, ax = plt.subplots(1, 1, figsize=figsize)

        num_plots = len(self._window_labels)
        df = self.data[self._window_labels]

        ax.axhline(y=0, ls='--', color='0.7')
        sns.violinplot(data=np.array(df.dropna()), bw=bw, cut=cut,
                       palette="Set3", ax=ax)
        #ax.boxplot(, labels=self._window_labels)
        title = 'Return Distribution btw ' + \
                self.start_date.strftime("%Y-%m-%d") + \
                ' ~ ' + self.end_date.strftime("%Y-%m-%d")
        ax.set_title(title)

        return

    def boxplot(self, bins=50, figsize=(8, 6)):
        '''
        Boxplot if the returns.
        '''
        fig, ax = plt.subplots(1, 1, figsize=figsize)

        num_plots = len(self._window_labels)
        df = self.data[self._window_labels]

        ax.axhline(y=0, ls='--', color='0.7')
        ax.boxplot(np.array(df.dropna()), labels=self._window_labels)
        title = 'Return Distribution btw ' + \
                self.start_date.strftime("%Y-%m-%d") + \
                ' ~ ' + self.end_date.strftime("%Y-%m-%d")
        ax.set_title(title)

        return

    def stats(self):
        all_stats = []
        for i, key in enumerate(self._window_labels):
            stats = {}
            series = self.data[key].dropna()
            n_points = len(series)
            stats['mean'] = np.mean(series)
            stats['std'] = np.std(series)
            stats['min'] = np.min(series)
            stats['max'] = np.max(series)
            stats['median'] = np.median(series)
            stats['5_percentile'] = np.percentile(series, 5)
            stats['95_percentile'] = np.percentile(series, 95)
            stats['n_points'] = n_points
            stats['frac_positive'] = np.sum(series > 0) / n_points
            stats['frac_negative'] = np.sum(series < 0) / n_points
            all_stats.append(stats)
        result = pd.DataFrame(all_stats, index=self._window_labels)
        result = result[['median', 'mean', 'std', 'min', 'max',
                         '5_percentile', '95_percentile',
                         'frac_positive', 'frac_negative', 'n_points']]

        return result

    def correlationAnalysis(self):
        pass
