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


class MomentumStrategy(BaseStrategy):
    def __init__(self, strategy_class: str, strategy_config: str):
        super().__init__(strategy_class=strategy_class, strategy_config=strategy_config)
        self.data_df = get_crypto_data_df(self.symbol, self.resample)
        self.backtest_df = datetime_slicer(self.backtest_time, self.data_df, self.start_date, self.end_date, self.count_to_now)

        # the part you return the prepare_data_param you need in run_backtest
        self.pos_ret_p = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("pos_ret_p", None)
        self.neg_ret_p = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("neg_ret_p", None)

        # the part you return the trading_data_param you need in run_backtest
        self.SL_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("SL_pct", None)
        self.TP_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("TP_pct", None)
    
    def run_backtest(self):
        # the part you design backtest trading logic
        # start with self.backtest_df and appending 
        # this is an example of self-designed indicators
        # 1. Input the strategy required data
        self.backtest_df['ret'] = self.backtest_df['close'].pct_change(periods=1)
        self.backtest_df['pos_ret'] = self.backtest_df['ret'].rolling(window=self.pos_ret_p).mean()
        self.backtest_df['neg_ret'] = self.backtest_df['ret'].rolling(window=self.neg_ret_p).mean()

        # 2. Using the Preparation data to define logic
        Pos_Ret = (self.backtest_df['pos_ret']>0)
        Neg_Ret = (self.backtest_df['neg_ret']<0)

        # 3. Define the Long/Short in Entry/Exit 
        self.backtest_df['entry_long'] = np.where(Pos_Ret, True, False)
        self.backtest_df['entry_short'] = np.where(Neg_Ret, True, False)
        self.backtest_df['exit_long']  = np.where(Pos_Ret, False, True)
        self.backtest_df['exit_short'] = np.where(Neg_Ret, False, True)

        # 4. Run Backtest
        super().run_backtest(self.backtest_df)
    