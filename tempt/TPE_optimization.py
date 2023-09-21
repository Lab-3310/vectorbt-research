# %%
import vectorbt as vbt
import datetime
import pandas as pd
import numpy as np
from hyperopt import fmin, tpe, hp, Trials
from functools import partial

# price data
start = '2019-01-01 UTC'
end = '2020-01-01 UTC'
btc_price = vbt.YFData.download('BTC-USD', start=start, end=end).get('Close')

# def target fuction


def optimize(params):
    fast_ma_length = int(params['fast_ma_length'])
    slow_ma_length = int(params['slow_ma_length'])

    # fast_ma slow_ma
    fast_ma = vbt.MA.run(btc_price, fast_ma_length, short_name='fast')
    slow_ma = vbt.MA.run(btc_price, slow_ma_length, short_name='slow')

    # signal
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)

    pf = vbt.Portfolio.from_signals(btc_price, entries, exits)
    total_return = -pf.total_return()

    return total_return


# def space
space = {
    'fast_ma_length': hp.quniform('fast_ma_length', 5, 50, 1),
    'slow_ma_length': hp.quniform('slow_ma_length', 10, 100, 1)
}

# %%

# Execute Bayesian optimization
trials = Trials()
best = fmin(fn=optimize, space=space, algo=tpe.suggest,
            max_evals=100, trials=trials)

# Print the best parameters and best profit
best_fast_ma_length = int(best['fast_ma_length'])
best_slow_ma_length = int(best['slow_ma_length'])
best_params_dict = {'fast_ma_length': best_fast_ma_length,
                    'slow_ma_length': best_slow_ma_length}

best_profit = -trials.best_trial['result']['loss']  # Corrected interpretation

print(f"最佳快线天数：{best_fast_ma_length}")
print(f"最佳慢线天数：{best_slow_ma_length}")
print(f"最佳利润：{best_profit}")


# %%
