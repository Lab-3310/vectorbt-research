import vectorbt as vbt
import pandas as pd 
import numpy as np
import datetime

symbols = ["BTC-USD"]
price = vbt.YFData.download(symbols, missing_index='drop').get('Close')

def show_stats(pf):
    """
    Show a plots report for a given portfolio using QuantStats.

    Parameters:
    pf (QuantStats): The QuantStats portfolio object to generate a plots report for.

    Returns:
    None
    """
    vbt.settings.array_wrapper.freq = 'D'
    pf.qs.plots_report()
    return None

