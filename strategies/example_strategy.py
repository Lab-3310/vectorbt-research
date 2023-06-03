import os, sys
sys.path.insert(1, os.path.dirname(__file__) + '/..')

import talib as ta
import numpy as np
import pandas as pd
import vectorbt as vbt
from datetime import datetime
import plotly.express as px

import types_enums.base_strategy_enum as base_strategy_enum

from base_strategy import BaseStrategy
from vbt_handler.vbt_support import vbt_saver_printer
from handler.backtest_handler import datetime_slicer
from handler.crypto_px_handler import get_crypto_data_df
from types_enums.vbt_enum import *

import warnings
warnings.filterwarnings("ignore")


class ExampleStrategy(BaseStrategy):
    def __init__(self, strategy_class: str, strategy_config: str):
        super().__init__(strategy_class=strategy_class, strategy_config=strategy_config)
        self.data_df = get_crypto_data_df(self.symbol, self.use_spot, self.resample)
        self.backtest_df = datetime_slicer(self.backtest_time, self.data_df, self.start_date, self.end_date, self.count_to_now)
        
        # the part you return the prepare_data_param you need in run_backtest
        self.er_p = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("er_p", None)
        self.zscore_p = self._config.get(base_strategy_enum.PREPARE_DATA_PARAM, {}).get("zscore_p", None)

        # the part you return the trading_data_param you need in run_backtest
        self.SL_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("SL_pct", None)
        self.TP_pct = self._config.get(base_strategy_enum.TRADING_DATA_PARAM, {}).get("TP_pct", None)

    def run_backtest(self):
        super().run_backtest()
        # the part you design backtest trading logic
        # start with self.backtest_df and appending 
        # 1. Input the strategy required data
        self.backtest_df["price_delta"] = (self.backtest_df["close"] - self.backtest_df["close"].shift(1))
        self.backtest_df["total_price_delta"] = (self.backtest_df["close"] - self.backtest_df["close"].shift(self.er_p))
        self.backtest_df["delta_abs_sum"] = ta.SUM(self.backtest_df["price_delta"].abs(), timeperiod=self.er_p)
        self.backtest_df["efficiency_ratio"] = self.backtest_df["total_price_delta"]/self.backtest_df["delta_abs_sum"]
        self.backtest_df["prev_efficiency_ratio"] = self.backtest_df["efficiency_ratio"].shift(1)
        self.backtest_df["efficiency_ratio_avg"] = ta.SMA(self.backtest_df["efficiency_ratio"], timeperiod=self.er_p)
        self.backtest_df["efficiency_ratio_stddev"] = ta.STDDEV(self.backtest_df["efficiency_ratio"], timeperiod=self.er_p)
        self.backtest_df["efficiency_ratio_zscore"] = (self.backtest_df["prev_efficiency_ratio"] - self.backtest_df["efficiency_ratio_avg"])/self.backtest_df["efficiency_ratio_stddev"]
        self.backtest_df["prev_efficiency_ratio_zscore"] = self.backtest_df["efficiency_ratio_zscore"].shift(1)

        # 2. Using the Preparation data to define logic 
        CrossUp_00 = (self.backtest_df['efficiency_ratio_zscore'] >= 0.0) & (self.backtest_df['prev_efficiency_ratio_zscore'] < 0.0)
        CrossUp_01 = (self.backtest_df['efficiency_ratio_zscore'] >= 1.0) & (self.backtest_df['prev_efficiency_ratio_zscore'] < 1.0)
        CrossUp_02 = (self.backtest_df['efficiency_ratio_zscore'] >= 2.0) & (self.backtest_df['prev_efficiency_ratio_zscore'] < 2.0)
        CrossUp_03 = (self.backtest_df['efficiency_ratio_zscore'] >= 3.0) & (self.backtest_df['prev_efficiency_ratio_zscore'] < 3.0)

        CrossDown_00 = (self.backtest_df['efficiency_ratio_zscore'] <= 0.0) & (self.backtest_df['prev_efficiency_ratio_zscore'] > 0.0)
        CrossDown_n01 = (self.backtest_df['efficiency_ratio_zscore'] <= -1.0) & (self.backtest_df['prev_efficiency_ratio_zscore'] > -1.0)
        CrossDown_n02 = (self.backtest_df['efficiency_ratio_zscore'] <= -2.0) & (self.backtest_df['prev_efficiency_ratio_zscore'] > -2.0)
        CrossDown_n03 = (self.backtest_df['efficiency_ratio_zscore'] <= -3.0) & (self.backtest_df['prev_efficiency_ratio_zscore'] > -3.0)    

        # 3. Define the Long/Short in Entry/Exit 
        self.backtest_df['entry_long'] = np.where(CrossUp_01,True, False)
        self.backtest_df['entry_short'] = np.where(CrossDown_n01 ,True, False)

        self.backtest_df['exit_long'] = np.where(CrossUp_03 | CrossDown_00,True, False)
        self.backtest_df['exit_short'] = np.where(CrossDown_n03 | CrossUp_00,True, False) 

        # 4. Run VectorBT backtest
        vbt_func = vbt.Portfolio.from_signals(
            init_cash=self.capital,
            sl_stop = self.SL_pct,
            tp_stop = self.TP_pct,
            close = self.selfbacktest_df[CLOSE],
            entries = self.backtest_df[ENTRY_LONG],
            exits = self.backtest_df[EXIT_SHORT],
            short_entries = self.backtest_df[ENTRY_SHORT],
            short_exits = self.backtest_df[ENTRY_SHORT],
            direction = 'both',
            accumulate = False,
            freq = 'd' # this will change either II use what resample_p
        )
        vbt_report = vbt_func.plot()

        # position
        position = vbt_func.asset_flow()
        position_df = pd.DataFrame({DATETIME:position.index, POSITION:position.values})
        # plot position
        positionfig = px.line(position_df, x=DATETIME, y=POSITION)
        positionfig.show()

        # printing 
        print("---------")
        print(f"Running {self._strategy_class} in config: {self._strategy_config} trading {self.asset_class} on {self.exchange} in {self.symbol} {self.resample}")
        print("Stats")
        print("---------")
        vbt_report.show()
        stats_df = vbt_func.stats()
        print(stats_df)
        print("---------")
        print("strategy metric df")
        print(self.backtest_df.tail(5))
        print("---------")
        asset_return = vbt_func.asset_returns()
        asset_value  = vbt_func.asset_value()
        cumulative_returns = vbt_func.cumulative_returns()
        vbt_saver_printer(self._strategy_class, self._strategy_config, stats_df, position_df, self.backtest_df, vbt_func, asset_return, asset_value, cumulative_returns)
                    

