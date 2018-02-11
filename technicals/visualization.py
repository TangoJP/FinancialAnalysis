import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bokeh
import math

# ***Most likely, do not implement a single candlestick object
# ***and simply use the group object below
class CandleStick:
    '''
    Implementation of a single candlestick.
    '''
    def __init__(self, open_=None, close_=None, low_=None, high_=None):
        self.open_ = open_
        self.close_ = close_
        self.low_ = low_
        self.high_ = high_
        self.uptick_ = self.high_ - max(self.close_, self.open_)
        self.downpick_ = min(self.close_, self.open_) - self.low_
        self.boxlength_ = abs(self.close_ - self.open_)
        self.range_ = self.high_ - self.low_

class CandleSticks:
    '''
    A group of CandleSticks
    '''
    def __init__(self, data, period=1):
        '''
        Read in data, create candle sticks for the specified period.

        data : DataFrame
            time series with time on the index. It must contain columns:
            'open', 'close', 'low', and 'high.'
        period : int
            number of periods to aggregate
        '''
        fields = ['open', 'close', 'high', 'low',
                  'uptick', 'downpick', 'boxlength', 'range']
        candlesticks = pd.DataFrame(columns=fields)

        # Aggregate specified number of periods

        # Create a CandleStick object for each aggregated period

        # Create new DataFrame with new time index (last time points of the
        # aggregate time period) with new open, close, low, and high

        pass

    def plot(self, period=None):
        '''
        plot candlestick chart for the object.
        '''
        pass
