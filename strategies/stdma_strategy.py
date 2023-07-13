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


class STDMAStrategy(BaseStrategy):
    def __init__(self, strategy_class: str, strategy_config: str):
        super().__init__(strategy_class=strategy_class, strategy_config=strategy_config)
        self.data_df = get_crypto_data_df(self.symbol, self.resample)
        self.backtest_df = datetime_slicer(self.backtest_time, self.data_df, self.start_date, self.end_date, self.count_to_now)

        # the part you return the prepare_data_param you need in run_backtest
        self.ret_p = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("ret_p", None)
        self.zscore_p = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("zscore_p", None)
        self.ma_p = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("ma_p", None)

        # the part you return the trading_data_param you need in run_backtest
        self.SL_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("SL_pct", None)
        self.TP_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("TP_pct", None)
    
    def run_backtest(self):
        # the part you design backtest trading logic
        # start with self.backtest_df and appending 
        # this is an example of self-designed indicators
        # 1. Input the strategy required data
        self.backtest_df['ret'] = self.backtest_df['close'].pct_change(periods=self.ret_p)
        self.backtest_df['std'] = ta.STDDEV(self.backtest_df['ret'], timeperiod=self.zscore_p)
        self.backtest_df['std_recent'] = ta.SMA(self.backtest_df['ret'], timeperiod=self.ma_p)
        self.backtest_df['std_above'] = (self.backtest_df['std_recent'] > self.backtest_df['std'])
        self.backtest_df['prev_std_above'] = self.backtest_df['std_above'].shift(1)

        self.backtest_df['close_zscore'] = (self.backtest_df['close'] - ta.SMA(self.backtest_df['close'], timeperiod=self.zscore_p)
                                         ) / ta.STDDEV(self.backtest_df["close"], timeperiod=self.zscore_p) 
        self.backtest_df['close_zscore_ma'] = ta.SMA(self.backtest_df["close_zscore"], timeperiod=self.ma_p)
        self.backtest_df['close_zscore_above'] = (self.backtest_df['close_zscore'] > self.backtest_df['close_zscore_ma'])
        self.backtest_df['prev_close_zscore_above'] = self.backtest_df['close_zscore_above'].shift(1)
  

        # 2. Using the Preparation data to define logic
        std_Up = (self.backtest_df['std_above']==1)
        std_Down = (self.backtest_df['std_above']==0)
        std_CrossUp = (self.backtest_df['prev_std_above']==0) & (self.backtest_df['std_above']==1)
        std_CrossDown = (self.backtest_df['prev_std_above']==1) & (self.backtest_df['std_above']==0)

        close_zscore_Up = (self.backtest_df['close_zscore_above']==1)
        close_zscore_Down = (self.backtest_df['close_zscore_above']==0)        
        close_zscore_CrossUp = (self.backtest_df['prev_close_zscore_above']==0) & (self.backtest_df['close_zscore_above']==1)
        close_zscore_CrossDown = (self.backtest_df['prev_close_zscore_above']==1) & (self.backtest_df['close_zscore_above']==0)
  

        # 3. Define the Long/Short in Entry/Exit 
        self.backtest_df['entry_long'] = np.where( (std_Down & close_zscore_Up), True, False)
        self.backtest_df['entry_short'] = np.where( (std_Up & close_zscore_Down), True, False)
        self.backtest_df['exit_long'] = np.where( (std_CrossUp & close_zscore_CrossDown), True, False)
        self.backtest_df['exit_short'] = np.where( (std_CrossDown & close_zscore_CrossUp), True, False)

        # 4. Run Backtest
        super().run_backtest(self.backtest_df)
    