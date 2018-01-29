import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import stock
from stock import Stock

class BaseAnalysis:
    def __init__(self, stock, start=None, end=None):
        if isinstance(stock, Stock):
            if (start is not None) and (end is not None):
                '''Raise Some exception that start/end dates were input'''
                print('Start/End won\'t be reset')
            stock = stock

        elif isinstance(stock, str):
            '''Include code to read in the Stock Object'''
            stock = Stock(stock, start=start, end=end)
            
        else:
            '''raise an InvalidInputType exception'''
            print('Invalid stock type')
            pass

        self.ticker = stock.ticker
        self.data = stock.data_table
        self.start_date = self.data.index.min()
        self.end_date = self.data.index.max()

    def plot(self, ax=None, figsize=None):
        if ax is None:
            if figsize is None:
                figsize = (5, 5)
            fig, ax = plt.subplots(1, 1, figsize=figsize)
        else:
            ax = ax
