import os, sys
sys.path.insert(1, os.path.dirname(__file__) + '/..')

import talib as ta
import numpy as np
import pandas as pd
import vectorbt as vbt
from datetime import datetime
import plotly.express as px

import types_enums.base_strategy_enum as base_strategy_enum

from strategies.base_strategy import BaseStrategy
from handler.backtest_handler import datetime_slicer
from handler.crypto_px_handler import get_crypto_data_df
from types_enums.vbt_enum import *

import warnings
warnings.filterwarnings("ignore")


class DoubleSmaExampleStrategy(BaseStrategy):
    def __init__(self, strategy_class: str, strategy_config: str):
        super().__init__(strategy_class=strategy_class, strategy_config=strategy_config)
        self.data_df = get_crypto_data_df(self.symbol, self.resample)
        self.backtest_df = datetime_slicer(self.backtest_time, self.data_df, self.start_date, self.end_date, self.count_to_now)

        # the part you return the prepare_data_param you need in run_backtest
        self.ma_p1 = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("ma_p1", None)
        self.ma_p2 = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("ma_p2", None)

        # the part you return the trading_data_param you need in run_backtest
        self.SL_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("SL_pct", None)
        self.TP_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("TP_pct", None)

    def init_vbt(self):
        vbt_func = vbt.Portfolio.from_signals(init_cash=self.capital, fees=self.fee, sl_stop=self.SL_pct, tp_stop=self.TP_pct, close=self.backtest_df[CLOSE], entries=self.backtest_df[ENTRY_LONG], exits=self.backtest_df[EXIT_SHORT], short_entries=self.backtest_df[ENTRY_SHORT], short_exits=self.backtest_df[EXIT_SHORT], direction='both', accumulate=False, freq='d')
        vbt_func.plot().show()
        position_df = pd.DataFrame({DATETIME:vbt_func.asset_flow().index, POSITION:vbt_func.asset_flow().values})
        position_fig = px.line(position_df, x=DATETIME, y=POSITION)
        position_fig.show()

        stats_df = vbt_func.stats()
        asset_return = vbt_func.asset_returns()
        asset_value = vbt_func.asset_value()
        cumulative_returns = vbt_func.cumulative_returns()

        return vbt_func, stats_df, asset_return, asset_value, cumulative_returns, position_df
    
    def run_backtest(self):
        super().run_backtest()
        # the part you design backtest trading logic
        # start with self.backtest_df and appending 
        # this is an example of double sma strategy
        # long when ma cross bullish, short in ma cross bearish
        
        # 1. Input the strategy required data
        self.backtest_df['ma_1'] = ta.SMA(self.backtest_df[CLOSE], timeperiod=self.ma_p1)
        self.backtest_df['ma_2'] = ta.SMA(self.backtest_df[CLOSE], timeperiod=self.ma_p2)
        self.backtest_df["prev_ma_1"] = self.backtest_df["ma_1"].shift(1)
        self.backtest_df["prev_ma_2"] = self.backtest_df["ma_2"].shift(1)


        # 2. Using the Preparation data to define logic 
        ma_crossup = (self.backtest_df['ma_1'] >= self.backtest_df['ma_2']) & (self.backtest_df['prev_ma_1'] < self.backtest_df['prev_ma_2'])
        ma_crossdown = (self.backtest_df['ma_1'] <= self.backtest_df['ma_2']) & (self.backtest_df['prev_ma_1'] > self.backtest_df['prev_ma_2'])

        # 3. Define the Long/Short in Entry/Exit 
        self.backtest_df['entry_long'] = np.where(ma_crossup, True, False)
        self.backtest_df['entry_short'] = np.where(ma_crossdown, True, False)
        self.backtest_df['exit_long'] = np.where(ma_crossdown, True, False)
        self.backtest_df['exit_short'] = np.where(ma_crossup, True, False) 

        # 4. Run VectorBT backtest
        vbt_func, stats_df, asset_return, asset_value, cumulative_returns, position_df = self.init_vbt()
        self.vbt_result(self._strategy_class, self._strategy_config, stats_df, position_df, self.backtest_df, vbt_func, asset_return, asset_value, cumulative_returns)
                    

