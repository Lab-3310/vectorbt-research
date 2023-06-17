import os
import json
import logging
import pandas as pd
import types_enums.base_strategy_enum as base_strategy_enum
from types_enums.vbt_enum import *

class BaseStrategy:
    def __init__(self, strategy_class: str, strategy_config: str):
        self._strategy_class = strategy_class
        self._strategy_config = strategy_config
        self.logger = logging.getLogger(f"Backtest_{self._strategy_class}_{self._strategy_config}")
        
        with open(f'{os.path.dirname(__file__)}/../strategies_config/{strategy_class}/{strategy_config}.json') as f:
            config = json.loads(f.read())
        self._config = config

    @property
    def capital(self):
        return self._config.get(base_strategy_enum.CAPITAL, None)
 
    @property
    def asset_class(self):
        return self._config.get(base_strategy_enum.ASSET_CLASS, None)

    @property
    def exchange(self):
        return self._config.get(base_strategy_enum.EXCHANGE, None)

    @property
    def symbol(self):
        return self._config.get(base_strategy_enum.SYMBOL, None)
    
    @property
    def fee(self):
        return self._config.get(base_strategy_enum.FEE, None)
    
    @property
    def resample(self):
        return self._config.get(base_strategy_enum.RESAMPLE, None)

    @property
    def backtest_time(self):
        return self._config.get(base_strategy_enum.BACKTEST_SETTING, {}).get(base_strategy_enum.BACKTEST_TIME, None)

    @property
    def start_date(self):
        return self._config.get(base_strategy_enum.BACKTEST_SETTING, {}).get(base_strategy_enum.START_DATE, None)

    @property
    def end_date(self):
        return self._config.get(base_strategy_enum.BACKTEST_SETTING, {}).get(base_strategy_enum.END_DATE, None)

    @property
    def count_to_now(self):
        return self._config.get(base_strategy_enum.BACKTEST_SETTING, {}).get(base_strategy_enum.COUNT_TO_NOW, None)

    def run_backtest(self):
        self.logger.info(f'Running Backtest - [{self._strategy_class=}, {self._strategy_config=}].')

    def vbt_result(self, strategy_class: str, strategy_config: str, stats_df: pd.DataFrame, position_df: pd.DataFrame, backtest_df: pd.DataFrame, vbt_func, asset_return: pd.DataFrame, asset_value: pd.DataFrame, cumulative_returns: pd.DataFrame):
        save_dir = f'{os.path.dirname(__file__)}/../backtest_result/{strategy_class}/{strategy_config}'
        os.makedirs(save_dir, exist_ok=True)
        # Saving dataframes to local file
        stats_df.to_csv(f'{save_dir}/{strategy_config}_stats_vbt.csv')
        position_df.to_csv(f'{save_dir}/{strategy_config}_position_vbt.csv')
        backtest_df.to_csv(f'{save_dir}/{strategy_config}_metric_df_vbt.csv')
        asset_return.to_csv(f'{save_dir}/{strategy_config}_asset_return_vbt.csv')
        asset_value.to_csv(f'{save_dir}/{strategy_config}_asset_value_vbt.csv')
        cumulative_returns.to_csv(f'{save_dir}/{strategy_config}_cumulative_returns_vbt.csv')
        trade_record = vbt_func.positions.records_readable
        trade_record.to_csv(f'{save_dir}/{strategy_config}_trade_pnl_vbt.csv')
        print('Backtest Results')
        print('---------')
        print(stats_df)
        print('---------')
        print(f'VBT Backtest Report in {strategy_class}/{strategy_config} Saved Success!')





