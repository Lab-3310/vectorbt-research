import vectorbt as vbt
import numpy as np

symbols = ["BTC-USD"]
price = vbt.YFData.download(symbols, missing_index='drop').get('Close')

def rolling_split(n: int, window_len: int, set_lens: int, left_to_right=False):

    (in_sample_prices, in_sample_dates), (out_sample_prices, out_sample_dates) = price.vbt.rolling_split(
        n=n,
        window_len=window_len,
        set_lens=(set_lens, ),
        left_to_right=left_to_right
        )

    return (in_sample_prices, in_sample_dates), (out_sample_prices, out_sample_dates)

def rolling_split_plot(n: int, window_len: int, set_lens: int, left_to_right=False, plot=True, trace_names=['in_sample', 'out_sample']):

    graph = price.vbt.rolling_split(
        n=n,
        window_len=window_len,
        set_lens=(set_lens, ),
        left_to_right=left_to_right,
        plot=plot,
        trace_names=trace_names
        )
    
    return graph

def in_sample_prices(n: int, window_len: int, set_lens: int, left_to_right=False):

    (in_sample_prices, in_sample_dates), (out_sample_prices, out_sample_dates) = price.vbt.rolling_split(
        n=n,
        window_len=window_len,
        set_lens=(set_lens, ),
        left_to_right=left_to_right
        )

    return in_sample_prices

def get_optimal(x):
    df = x[x.groupby('split_idx').idxmax()].index
    return print(df)

fast_ma, slow_ma = vbt.MA.run_combs(in_sample_prices(28, 360, 108), window=np.arange(1, 25), r=2, short_names=['fast', 'slow'])

entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

pf = vbt.Portfolio.from_signals(in_sample_prices(28, 360, 108), entries, exits)
res = pf.total_return()

get_optimal(res)