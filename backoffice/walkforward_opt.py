import vectorbt as vbt
import numpy as np



"""
(in_sample_prices, in_sample_dates), (out_sample_prices, out_sample_dates) = price.vbt.rolling_split(
    n=28,
    window_len=360,
    set_lens=(108, ),
    left_to_right=False
    )

"""
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