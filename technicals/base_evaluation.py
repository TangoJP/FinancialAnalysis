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

from base import TechnicalAnalysisCase

class CaseEvaluation:
    def __init__(self, TACase, metric):
        self.case = TACase
        self.metric = metric
        
