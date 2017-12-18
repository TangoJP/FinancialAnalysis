import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from stock import Stock
from base_analysis import BaseAnalysis

class PriceAnalysis(BaseAnalysis):
    def __init__(self, stock, start=None, end=None):
        super.__init__(self, stock, start=None, end=None)
