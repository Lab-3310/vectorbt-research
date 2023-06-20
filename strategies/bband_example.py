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
warnings.filterwarnings('ignore')


class BbandCrossExampleStrategy(BaseStrategy):
    def __init__(self, strategy_class: str, strategy_config: str):
        super().__init__(strategy_class=strategy_class, strategy_config=strategy_config)
        self.data_df = get_crypto_data_df(self.symbol, self.resample)
        self.backtest_df = datetime_slicer(self.backtest_time, self.data_df, self.start_date, self.end_date, self.count_to_now)

        # the part you return the prepare_data_param you need in run_backtest
        self.bband_p = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get('bband_p', None)
        self.bband_stddev = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get('bband_stddev', None)

        # the part you return the trading_data_param you need in run_backtest
        self.SL_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get('SL_pct', None)
        self.TP_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get('TP_pct', None)
    
    def run_backtest(self):
        # the part you design backtest trading logic
        # start with self.backtest_df and appending 
        # this is an example of bband cross strategy
        # open long when close crossup bband upper bband, open short when close crossdown bband lower bband
        # close long when close crossdown the bband bband, close short when close cross


        # 1. Input the strategy required data
        self.backtest_df[PREV_CLOSE] = self.backtest_df[CLOSE].shift(1)
        self.backtest_df['band_upper'], self.backtest_df['band_middle'], self.backtest_df['band_lower'] = ta.BBANDS(
            self.backtest_df[CLOSE],
            timeperiod = self.bband_p,
            nbdevup = self.bband_stddev,
            nbdevdn = self.bband_stddev,
        )
        self.backtest_df['prev_band_upper'] = self.backtest_df['band_upper'].shift(1)
        self.backtest_df['prev_band_lower'] = self.backtest_df['band_lower'].shift(1)

        #ljljdf

        # 2. Using the Preparation data to define logic 
        bband_upper_crossup = (self.backtest_df[CLOSE] >= self.backtest_df['band_upper']) & (self.backtest_df[PREV_CLOSE] < self.backtest_df['prev_band_upper'])
        bband_upper_crossdown = (self.backtest_df[CLOSE] <= self.backtest_df['band_upper']) & (self.backtest_df[PREV_CLOSE] > self.backtest_df['prev_band_upper'])
        bband_lower_crossdown = (self.backtest_df[CLOSE] <= self.backtest_df['band_lower']) & (self.backtest_df[PREV_CLOSE] > self.backtest_df['prev_band_lower'])
        bband_lower_crossup = (self.backtest_df[CLOSE] >= self.backtest_df['band_lower']) & (self.backtest_df[PREV_CLOSE] < self.backtest_df['prev_band_lower'])

        # 3. Define the Long/Short in Entry/Exit 
        self.backtest_df['entry_long'] = np.where(bband_upper_crossup, True, False)
        self.backtest_df['entry_short'] = np.where(bband_lower_crossdown, True, False)
        self.backtest_df['exit_long'] = np.where(bband_upper_crossdown, True, False)
        self.backtest_df['exit_short'] = np.where(bband_lower_crossup, True, False) 

        # 4. Run Backtest
        super().run_backtest(self.backtest_df)