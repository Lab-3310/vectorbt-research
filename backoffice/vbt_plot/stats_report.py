import vectorbt as vbt
import pandas as pd 
import numpy as np
import datetime
import os
import matplotlib.pyplot as plt


class startegy_stat:
    def __init__(self,pf) -> None:
        pass

    def show_recoard():
        return pf.orders.records_readable
    
    def show_position_plot():
        fig = pf.positions.plot()
        fig.write_image(os.path.expanduser('~/Systematic-Sherpa/script/image/position_plot.png')) # TODO 
        fig.show()
        return fig


    
    def show_stats():
        """
        Show a plots report for a given portfolio using QuantStats.

        Parameters:
        pf (QuantStats): The QuantStats portfolio object to generate a plots report for.
        type of pf :<vectorbt.portfolio.base.Portfolio at 0x14af11f40>

        Returns:
        None
        """
        vbt.settings.array_wrapper.freq = 'D'
        fig = pf.qs.plots_report()
        fig.write_image(os.path.expanduser('~/Systematic-Sherpa/script/image/plot_candle.png')) # TODO 
        fig.show()
        return fig


