import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from bokeh.plotting import figure, show, output_file
from bokeh.io import output_notebook

### The following code assumes the data contains columns named time, open, high,
### low, and close

def get_period_data(subset):
    subset = subset.reset_index()
    time_ = subset['time'].max()
    open_ = subset['open'].iloc[0]
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

def plot_candlestick(data, title_label=None):
    '''
    ### ***NEED to recalibrate the w parameter properly ####
    '''

    # Adopted from https://bokeh.pydata.org/en/latest/docs/gallery/candlestick.html
    df = data

    # Get boolean increase or decrease in the level for each row
    inc = df.close > df.open
    dec = df.open > df.close

    # set bar width to 60% of time interval in milliseconds
    time0 = data.index[0]
    time1 = data.index[1]
    time_interval = time1 - time0
    w = 0.6 * time_interval.seconds * 1000

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=800, title=title_label)
    p.xaxis.major_label_orientation = math.pi/4
    p.grid.grid_line_alpha=0.3

    p.segment(df.index, df.high, df.index, df.low, color="black")
    p.vbar(df.index[inc], w, df.open[inc], df.close[inc], fill_color="#D5E1DD", line_color="black")
    p.vbar(df.index[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black")

    output_notebook()#"candlestick.html", title="candlestick.py example")

    show(p)
