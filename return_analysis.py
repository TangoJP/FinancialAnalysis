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
                 windows=[10, 20, 50, 100, 200]):
        super().__init__(stock, start=start, end=end, return_type=return_type)

        # Initialize windows
        if all(isinstance(n, int) for n in windows):
            self.windows = windows
        else:
            '''Raise Exception'''
            print('Windows must be a list of integers')
            return

        # Create returns for each window
        for window in windows:
            key = '%dday_return' % window
            if return_type == 'linear':
                self.data['daily_return'] = \
                    (self.data['Close']/self.data['Close'].shift(window))-1
            else:
                self.data[key] = \
                    np.log(self.data['Close']/self.data['Close'].shift(window))

        window_labels = ['daily_return']
        for i, w in enumerate(self.windows):
            key = '%dday_return' % w
            window_labels.append(key)
        self._window_labels = window_labels

    def hist(self, bins=50, figsize=(18, 4)):
        fig = plt.figure(figsize=figsize)
        num_plots = len(self._window_labels)

        # Plot 1-day return
        ax1 = fig.add_subplot(1, num_plots, 1)
        sns.distplot(self.data['daily_return'].dropna(), ax=ax1)
        ax1.set_xlabel('1-day_return')

        # Plot X-day returns
        for i, w in enumerate(self.windows):
            key = '%dday_return' % w
            df = self.data[key]

            ax = fig.add_subplot(1, num_plots, i+2, sharex=ax1, sharey=ax1)
            sns.distplot(self.data[key].dropna(), ax=ax)
            ax.set_xlabel(key)

        plt.tight_layout()

        return

    def violinplot(self, bw=0.2, cut=1, figsize=(8, 6)):
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
            stats['mean'] = np.mean(series)
            stats['std'] = np.std(series)
            stats['min'] = np.min(series)
            stats['max'] = np.max(series)
            stats['median'] = np.median(series)
            stats['5_percentile'] = np.percentile(series, 5)
            stats['95_percentile'] = np.percentile(series, 95)
            all_stats.append(stats)
        result = pd.DataFrame(all_stats, index=self._window_labels)
        result = result[['median', 'mean', 'std', 'min', 'max',
                         '5_percentile', '95_percentile']]

        return result
