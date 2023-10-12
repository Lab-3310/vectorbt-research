import vectorbt as vbt
import pandas as pd 
import numpy as np
import datetime


def show_stats(pf):
    """
    Show a plots report for a given portfolio using QuantStats.

    Parameters:
    pf (QuantStats): The QuantStats portfolio object to generate a plots report for.
    type of pf :<vectorbt.portfolio.base.Portfolio at 0x14af11f40>

    Returns:
    None
    """
    vbt.settings.array_wrapper.freq = 'D'
    pf.qs.plots_report()
    return None

