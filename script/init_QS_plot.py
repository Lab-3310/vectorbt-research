import os
import sys

sys.path.insert(1, f"{os.path.dirname(__file__)}/..") # TODP path fix general way

from backoffice.vbt_plot.stats_report import startegy_stat

def main():
    # sample strategy
    price = vbt.YFData.download('BTC-USD').get('Close')

    fast_ma = vbt.MA.run(price, 10)
    slow_ma = vbt.MA.run(price, 50)
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)

    pf = vbt.Portfolio.from_signals(price, entries, exits, init_cash=100)
    stat_activate = startegy_stat(pf)
    stat_activate.show_stats()


if __name__ == '__main__':
    main()
