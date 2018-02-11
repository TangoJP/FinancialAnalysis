import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bokeh
import math

### The following code assumes the data contains columns named time, open, high,
### low, and close

def get_period_data(subset):
    subset = subset.reset_index()
    time_ = subset['time'].max()
    open_ = subset['open'].iloc[-1]
    high_ = subset['high'].max()
    low_ = subset['low'].min()
    close_ = subset['close'].iloc[-1]
    period_data =  {'time': time_,
                    'open': open_,
                    'high': high_,
                    'low':low_,
                    'close': close_}
    return period_data

def aggregate_periods(data, period=20):
    num_rows = len(data)
    times = []
    opens = []
    highs = []
    lows = []
    closes = []

    counter = 0
    while counter < num_rows:
        subset = data.iloc[counter:(counter+period-1)]
        period_data = get_period_data(subset)
        times.append(period_data['time'])
        opens.append(period_data['open'])
        highs.append(period_data['high'])
        lows.append(period_data['low'])
        closes.append(period_data['close'])
        counter += period
    aggregated = pd.DataFrame({'time': times,
                               'open': opens,
                               'high': highs,
                               'low':lows,
                               'close': closes})
    aggregated = aggregated[['time', 'open', 'high', 'low', 'close']].set_index('time')
    return aggregated
