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
#from moving_average import MA, SMA, MACollection

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
        subset = data.iloc[counter:(counter + period - 1)]
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

def plot_candlestick1(data, ax=None, title_label=None):
    '''
    matplotlib implementation.
    '''
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(16,8))
    candlestick2_ohlc(ax, data['open'], data['high'], data['low'], data['close'],
                      width=1)

    return

def plot_candlestick(data, p=None, title_label=None, show_plot=True,
                     plot_height=300, plot_width=800):
    '''
    bokeh implementation

    ### ***NEED to recalibrate the w parameter properly ####
    '''

    # Adopted from https://bokeh.pydata.org/en/latest/docs/gallery/candlestick.html
    if 'numerical_index' not in data.columns:
        data.loc[:, 'numerical_index'] = [i for i in range(len(data))]
    df = data[['numerical_index', 'open', 'high', 'low', 'close']]

    # Get boolean increase or decrease in the level for each row
    inc = df.close > df.open
    dec = df.open > df.close

    # set bar width to 60% of time interval in milliseconds
    time0 = data.numerical_index[0]
    time1 = data.numerical_index[1]
    time_interval = time1 - time0
    w = 0.6*time_interval #0.6 * time_interval.seconds * 1000

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    if p is None:
        p = create_default_panel(plot_height=plot_height, plot_width=plot_width)

    p.segment(df.numerical_index, df.high,
              df.numerical_index, df.low, color="black")
    p.vbar(df.numerical_index[inc], w, df.open[inc], df.close[inc],
                                    fill_color="#D5E1DD", line_color="black")
    p.vbar(df.numerical_index[dec], w, df.open[dec], df.close[dec],
                                    fill_color="#F2583E", line_color="black")

    # This will skip the datetime gap by using numerical index
    x_replacement_dictionary = {
                        i : date.strftime('%Y-%m-%d %-H:%M')
                        for i, date in enumerate(data.index)}
    p.xaxis.major_label_overrides = x_replacement_dictionary

    if show_plot:
        output_notebook()#"candlestick.html", title="candlestick.py example")
        show(p)
        return
    else:
        return p

def create_default_panel(title=None, plot_height=300, plot_width=800):
    TOOLS = "pan,wheel_zoom,box_zoom,zoom_in,zoom_out,hover,reset,save"
    p = figure(title=title,
               tools=TOOLS,
               plot_height=plot_height,
               plot_width=plot_width)
    p.grid.grid_line_alpha=0.3
    p.xaxis.major_label_orientation = math.pi/4

    return p

def eval_metric_performance(series, metric_col, eval_periods=[1,5,10]):
    '''
    INPUTS:
    =======
    series : pd.Series
        Vector containing the closing price, opening price, etc.
    metric_col : pd.Series
        Vector containing the metric information. +1 indicates buy and -1
        indicates sell signal.
    eval_periods : list/array
        A list/array containing the length of period to evaluate performance for.
    '''
    df = pd.concat([series, metric_col], axis=1).reset_index()
    series_name = series.name
    metric_name = metric_col.name

    for period in eval_periods:
        signal_indices = [i
            for i in df[(df[metric_name] == 1) | (df[metric_name] == -1)].index
            if (i+period) in df.index]
        return_indices = [i+period
            for i in signal_indices
            if (i+period) in df.index]

        period_returns = 100*((np.array(df.loc[return_indices, series_name])\
                            / np.array(df.loc[signal_indices, series_name])) -1)

        col_label = str(period) + 'period_return'
        df[col_label] = 0
        df.loc[signal_indices, col_label] = period_returns

    return df

def plot_performance_mpl(df, metric_col, bins=10, eval_periods=[1,5,10],
                         colors=['skyblue', 'salmon']):
    num_periods = len(eval_periods)
    num_cols = 6
    if (num_periods % 5) == 0:
        num_rows = num_periods / num_cols
    else:
        num_rows = (num_periods // num_cols) + 1

    color1 = colors[0]
    color2 = colors[1]
    fig1 = plt.figure(figsize=(4*num_cols, 4* num_rows))
    fig2 = plt.figure(figsize=(4*num_cols, 4* num_rows))
    for i, period in enumerate(eval_periods):
        col_label = str(period) + 'period_return'

        ax1 = fig1.add_subplot(num_rows, num_cols, i+1)
        ax1.axvline(x=0, ls=':', color='0.7')
        golden_return = df[df[metric_col] == 1].loc[:, col_label]
        golden_return.plot(kind='hist', bins=bins, color=color1, alpha=0.6, ax=ax1)
        bound1 = 1.1*max(abs(max(golden_return)), abs(min(golden_return)))
        ax1.set_title(col_label)
        ax1.set_xlabel("% return")
        ax1.set_ylabel('Frequency')
        ax1.set_xlim([-bound1, bound1])
        plt.tight_layout()

        ax2 = fig2.add_subplot(num_rows, num_cols, i+1)
        ax2.axvline(x=0, ls=':', color='0.7')
        death_return = df[df[metric_col] == -1].loc[:, col_label]
        death_return.plot(kind='hist', bins=bins, color=color2, alpha=0.6, ax=ax2)
        bound2 = 1.1*max(abs(max(death_return)), abs(min(death_return)))
        ax2.set_title(col_label)
        ax2.set_xlabel("% return")
        ax2.set_ylabel('Frequency')
        ax2.set_xlim([-bound2, bound2])
        plt.tight_layout()

        print('='*5, '%s' % col_label, '='*15)
        print('Golden Cross Return (%%): %.2f +/- %.2f' \
                            % (np.mean(golden_return), np.std(golden_return)))
        print('Death  Cross Return (%%): %.2f +/- %.2f' \
                            % (np.mean(death_return), np.std(death_return)))
    print('='*5, 'Numer of Cases for %s' % metric_col, '='*5)
    print('Total Numbe of Periods: %d' % len(df))
    print('Number of Golden Crosses: %d' % len(golden_return))
    print('Number of Golden Crosses: %d' % len(death_return))
    return
