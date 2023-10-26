import vectorbt as vbt
import pandas as pd 
import numpy as np
import datetime
import os
import matplotlib.pyplot as plt


class startegy_stat:
    def __init__(self, pf_init) -> None:
        self.pf = pf_init

    def show_recoard(self):
        return self.pf.orders.records_readable
    
    def show_position_plot(self):
        fig = self.pf.positions.plot()
        fig.write_image(os.path.expanduser('~/Systematic-Sherpa/script/image/position_plot.png')) # TODO 
        fig.show()
        return fig

    def show_stats(self):
        """
        Show a plots report for a given portfolio using QuantStats.
        """
        vbt.settings.array_wrapper.freq = 'D'
        fig = self.pf.qs.plots_report()
        fig.write_image(os.path.expanduser('~/Systematic-Sherpa/script/image/plot_candle.png')) # TODO 
        fig.show()
        return fig


