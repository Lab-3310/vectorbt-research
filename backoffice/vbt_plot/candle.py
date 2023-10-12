import vectorbt as vbt
import pandas as pd 
import numpy as np
import datetime

#symbols = ["BTC-USD"]


def candal_graph(symbols):
    """
    Generate a candlestick chart for a list of symbols using Yahoo Finance data.

    Parameters:
    symbols (list of str): A list of stock symbols to fetch data for and create the candlestick chart.
    ex:'BTC-USD'

    Returns:
    None
    """
    price_close = vbt.YFData.download(symbols).get('Close')
    price_high = vbt.YFData.download(symbols).get('High')
    price_open = vbt.YFData.download(symbols).get('Open')
    price_low = vbt.YFData.download(symbols).get('Low')
    price_volume = vbt.YFData.download(symbols).get('Volume')
    
    df = pd.DataFrame({
        'my_open1': price_open,
        'my_high2': price_high,
        'my_low3': price_low,
        'my_close4': price_close,
        'my_volume5': price_volume
    })
    my_column_names = dict(
        open='my_open1',
        high='my_high2',
        low='my_low3',
        close='my_close4',
        volume='my_volume5',
    )

    ohlcv_acc = df.vbt.ohlcv(freq='d', column_names=my_column_names)
    ohlcv_acc.plot()

    return ohlcv_acc.plot()
