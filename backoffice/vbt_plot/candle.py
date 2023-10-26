import vectorbt as vbt
import pandas as pd 
import numpy as np
import datetime
import os, sys 
#symbol = ["BTC-USD"]

def get_trade_example_plot():
    # fig = price.vbt.plot(trace_kwargs=dict(name='Close'))
    # fast_ma.ma.vbt.plot(trace_kwargs=dict(name='Fast MA'), fig=fig)
    # slow_ma.ma.vbt.plot(trace_kwargs=dict(name='Slow MA'), fig=fig)
    # pf.positions.plot(close_trace_kwargs=dict(visible=False), fig=fig)
    pass

def get_yearly_return_plot(pf, with_benchmark=True):
    price = vbt.YFData.download('BTC-USD').get('Close')
    returns = price.vbt.to_returns()
    if with_benchmark:
        fig = pf.qs.plot_yearly_returns()
    else:
        fig = returns.vbt.returns.qs.plot_yearly_returns()
    return fig

def get_return_and_mdd(returns):
    fig = returns.vbt.returns.qs.plots_report()
    return fig

def get_monthly_metric_plot(pf):
    fig = pf.qs.plots_report()
    return fig

def candle_graph(symbol, show = False):
    """
    Generate a candlestick chart for a list of symbol using Yahoo Finance data.

    Parameters:
    symbol (list of str): A list of stock symbol to fetch data for and create the candlestick chart.
    ex:'BTC-USD'

    Returns:
    None
    """
    # TODO plot width, height
    price_close = vbt.YFData.download(symbol).get('Close')
    price_high = vbt.YFData.download(symbol).get('High')
    price_open = vbt.YFData.download(symbol).get('Open')
    price_low = vbt.YFData.download(symbol).get('Low')
    price_volume = vbt.YFData.download(symbol).get('Volume')
    
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
    fig = ohlcv_acc.plot()
    fig.write_image(os.path.expanduser('~/Systematic-Sherpa/script/image/plot_candle.png')) # TODO 
    fig.show()

    return fig
