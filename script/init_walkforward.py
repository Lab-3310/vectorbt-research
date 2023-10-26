# import 
import vectorbt as vbt
import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(1,f'{os.path.dirname(__file__)}/..')

from backoffice.walk_forward.walkforward_opt_instance import WalkForwardOpt
import backoffice.vbt_plot.optimize_plot as optplot


def main():
    symbols = ["BTC-USD"]
    data = vbt.YFData.download(symbols, missing_index='drop').get('Close')

    w = WalkForwardOpt()
    w.rolling_split_plot(data, 28, 360, 108).show() # Visiualization of current trunk split.
    price = w.in_sample_prices(data, 28, 360, 108) # Get in-sample prices from splitted trunks.

    fast_ma, slow_ma = vbt.MA.run_combs(price, window=np.arange(1, 25), r=2, short_names=['fast', 'slow'])
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)

    pf = vbt.Portfolio.from_signals(price, entries, exits)
    res = pf.total_return()

    w.get_optimal(res) # Show optimal parameters in every trunk.

    res_df = pd.DataFrame(res).reset_index()

    for i in range(28):
        optplot.two_parameter_plot(res_df[res_df['split_idx'] == i], "total_return", "fast_window", 'slow_window', show = False)

    # n = int(input('Which trunk would you like to see? '))
    # optplot.two_parameter_plot(res_df[res_df['split_idx'] == n], "total_return", "fast_window", 'slow_window')

if __name__ == '__main__':
    main()
