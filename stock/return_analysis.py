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
                 windows=[1, 10, 20, 50, 100, 200]):
        super().__init__(stock, start=start, end=end)
        '''
        return_type : str
            If 'linear', linear return will be used. Otherwise, it's set
            to log return.
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
        window_labels_current = []
        window_labels_future = []
        for window in windows:
            key1 = '-%dday_return' % window
            key2 = '+%dday_return' % window
            window_labels_current.append(key1)
            window_labels_future.append(key2)

            if self.return_type == 'linear':
                self.data[key1] = \
                    (self.data['Close']/self.data['Close'].shift(window))-1
                self.data[key2] = \
                    (self.data['Close'].shift(-1*window)/self.data['Close'])-1
            else:
                self.data[key1] = \
                    np.log(self.data['Close']/self.data['Close'].shift(window))
                self.data[key2] = \
                    np.log(self.data['Close'].shift(-1*window)/self.data['Close'])
        self._window_labels_current = window_labels_current[::-1]
        self._window_labels_future = window_labels_future
        self._window_labels_all = window_labels_current[::-1]\
                                + window_labels_future

    def print_info(self):
        n_points = len(self.data['Close'])
        n_na = np.sum(self.data['Close'].isnull())

        print('=='*6, '%s Basic Info' % self.ticker, '=='*6)
        print('Start Date - %s' % self.start_date.strftime("%Y-%m-%d"))
        print(' End  Date - %s' % self.end_date.strftime("%Y-%m-%d"))
        print('Number of data points - %d' % n_points)
        print('Number of missing data points - %d' % n_na)

    def plot(self, figsize=(18, 4), include='future'):
        '''
        Plot returns against time.
        '''
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        if include == 'future':
            self.data[self._window_labels_future].plot(ax=ax, alpha=0.5)
        elif include == 'all':
            self.data[self._window_labels_all].plot(ax=ax, alpha=0.5)
        else:
            self.data[self._window_labels_current].plot(ax=ax, alpha=0.5)
        return

    def hist(self, bins=50, figsize=(18, 4)):
        '''
        Histogram of the returns.
        '''
        fig = plt.figure(figsize=figsize)
        num_plots = len(self._window_labels_future)

        # Plot X-day returns
        for i, w in enumerate(self.windows):
            key = '+%dday_return' % w
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

        num_plots = len(self._window_labels_future)
        df = self.data[self._window_labels_future]

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

        num_plots = len(self._window_labels_future)
        df = self.data[self._window_labels_future]

        ax.axhline(y=0, ls='--', color='0.7')
        ax.boxplot(np.array(df.dropna()), labels=self._window_labels_future)
        title = 'Return Distribution btw ' + \
                self.start_date.strftime("%Y-%m-%d") + \
                ' ~ ' + self.end_date.strftime("%Y-%m-%d")
        ax.set_title(title)

        return

    def stats(self):
        all_stats = []
        for i, key in enumerate(self._window_labels_future):
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
        result = pd.DataFrame(all_stats, index=self._window_labels_future)
        result = result[['median', 'mean', 'std', 'min', 'max',
                         '5_percentile', '95_percentile',
                         'frac_positive', 'frac_negative', 'n_points']]

        return result

    def all_correlations(self):
        '''
        Calculate correlation coefficients among all the return columns
        '''
        df = pd.DataFrame(index=self._window_labels_all,
                          columns=self._window_labels_all)
        for wind1 in self._window_labels_all:
            for wind2 in self._window_labels_all:
                df.loc[wind1, wind2] =\
                        self.data[wind1].corr(self.data[wind2])

        return df.astype('float')

    def current_future_correlations(self):
        '''
        Calculate correlation coefficient between the current and future
        returns.
        '''
        df = pd.DataFrame(index=self._window_labels_current,
                          columns=self._window_labels_future)
        for current_window in self._window_labels_current:
            for future_window in self._window_labels_future:
                df.loc[current_window, future_window] =\
                        self.data[current_window].corr(self.data[future_window])

        return df.astype('float')

    def calculate_conditional_return(self, past_window=1, future_window=5,
                                     selection=[-0.1, 0.1], graph=True):
        if (past_window not in self.windows) or (future_window not in self.windows):
            print('Window input(s) invalid.')
            return
        if selection[0] > selection[1]:
            print('First entry of \'selection\' larger than the second.\
                   Selection must be set as [min, max].')

        past_name = '-%dday_return' % past_window
        past = self.data[past_name]
        if isinstance(selection, tuple):
            past_selection = past[(past > selection[0]) & (past < selection[1])]
        else:
            past_selection = past[(past >= selection[0]) & (past <= selection[1])]
        selection_indices = past_selection.index

        future_name = '+%dday_return' % future_window
        future = self.data[future_name]
        future_selection = future.loc[selection_indices]

        print('%d-return of selection: %.3f +/- %.3f'\
              % (future_window, future_selection.mean(), future_selection.std()))
        future_selection.plot(kind='hist', bins=50)
