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


class DMIStrategy(BaseStrategy):
    def __init__(self, strategy_class: str, strategy_config: str):
        super().__init__(strategy_class=strategy_class, strategy_config=strategy_config)
        self.data_df = get_crypto_data_df(self.symbol, self.resample)
        self.backtest_df = datetime_slicer(self.backtest_time, self.data_df, self.start_date, self.end_date, self.count_to_now)

        # the part you return the prepare_data_param you need in run_backtest
        self.dm_p = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("dm_p", None)
        self.di_p = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("di_p", None)

        # the part you return the trading_data_param you need in run_backtest
        self.SL_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("SL_pct", None)
        self.TP_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("TP_pct", None)
    
    def run_backtest(self):
        # the part you design backtest trading logic
        # start with self.backtest_df and appending 
        # this is an example of self-designed indicators
        # 1. Input the strategy required data
        self.backtest_df['recent_high'] = self.backtest_df['high'].rolling(self.dm_p).max()
        self.backtest_df['recent_low'] = self.backtest_df['low'].rolling( self.dm_p).min()
        self.backtest_df['last_high'] = self.backtest_df['recent_high'].shift(self.dm_p)
        self.backtest_df['last_low'] = self.backtest_df['recent_low'].shift( self.dm_p)
        self.backtest_df['last_close'] = self.backtest_df['close'].shift(self.dm_p)

        self.backtest_df['+dm'] = self.backtest_df['recent_high'] - self.backtest_df['last_high']
        self.backtest_df['-dm'] = self.backtest_df['recent_low'] - self.backtest_df['last_low']

        self.backtest_df['tr1'] = self.backtest_df['recent_high'] - self.backtest_df['recent_low']
        self.backtest_df['tr2'] = self.backtest_df['recent_high'] - self.backtest_df['last_close']
        self.backtest_df['tr3'] = self.backtest_df['recent_low'] - self.backtest_df['last_close']
        self.backtest_df['tr'] = self.backtest_df[['tr1', 'tr2', 'tr3']].max(axis='columns')
        
        self.backtest_df['+di'] = self.backtest_df['+dm'].rolling(self.di_p).mean()/self.backtest_df['tr'].rolling(self.di_p).mean()
        self.backtest_df['-di'] = self.backtest_df['-dm'].rolling(self.di_p).mean()/self.backtest_df['tr'].rolling(self.di_p).mean()

        self.backtest_df['prev_+di'] = self.backtest_df['+di'].shift(1)
        self.backtest_df['prev_-di'] = self.backtest_df['-di'].shift(1)

        # 2. Using the Preparation data to define logic
        CrossUp = (self.backtest_df['prev_+di'] < self.backtest_df['prev_-di']) & (
                   self.backtest_df['+di'] > self.backtest_df['-di'])

        CrossDown = (self.backtest_df['prev_+di'] > self.backtest_df['prev_-di']) & (
                     self.backtest_df['+di'] < self.backtest_df['-di'])


        # 3. Define the Long/Short in Entry/Exit 
        self.backtest_df['entry_long'] = np.where(CrossUp, True, False)
        self.backtest_df['entry_short'] = np.where(CrossDown, True, False)
        self.backtest_df['exit_long'] = np.where(CrossDown, True, False)
        self.backtest_df['exit_short'] = np.where(CrossUp, True, False)

        # 4. Run Backtest
        super().run_backtest(self.backtest_df)