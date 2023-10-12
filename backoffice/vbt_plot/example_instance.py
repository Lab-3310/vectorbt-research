import vectorbt as vbt
import pandas as pd 
import numpy as np

"""
USER 

import VbtHandler
symbol = 'BTC-USD'
vbt_handler = VbtHandler(symbol, init_capital)

vbt_handler.get_low_price()

vbt_handler.get_yearly_return()

"""


class VbtHandler:

    def __init__(self, symbol: str, init_capital: int=1000):
        self.symbol = symbol
        self.capital = init_capital

    def get_open_price(self):
        return vbt.YFData.download(self.symbol).get('Open')

    def get_high_price(self):
        return vbt.YFData.download(self.symbol).get('High')

    def get_low_price(self):
        return vbt.YFData.download(self.symbol).get('Low')

    def get_close_price(self):
        return vbt.YFData.download(self.symbol).get('Close')

    def get_volume_price(self):
        return vbt.YFData.download(self.symbol).get('Volume')
    
    def get_pf_from_signal(self):
        """
        this is an example
        """
        fast_ma = vbt.MA.run(self.get_close_price, 10)
        slow_ma = vbt.MA.run(self.get_close_price, 50)
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)
        pf = vbt.Portfolio.from_signals(self.get_close_price, entries, exits, init_cash=self.capital)
        return pf
    
    def get_trading_records(self):
        pf = self.get_pf_from_signal
        result = pf.orders.records_readable
        return result
    
    def get_trading_plot(self):
        pf = self.get_pf_from_signal
        price = self.get_close_price
        fig = price.vbt.plot(trace_kwargs=dict(name='Close'))
        result = pf.positions.plot(close_trace_kwargs=dict(visible=False), fig=fig)
        return result

    def get_yearly_return(self, with_benchmark=True):
        price = self.get_close_price
        pf = self.get_pf_from_signal
        returns = price.vbt.to_returns()
        if with_benchmark:
            fig = pf.qs.plot_yearly_returns()
        else:
            fig = returns.vbt.returns.qs.plot_yearly_returns()
        return fig

        


