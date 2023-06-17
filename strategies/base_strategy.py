import os
import json
import logging
import pandas as pd
import types_enums.base_strategy_enum as base_strategy_enum
from types_enums.vbt_enum import *
import plotly.express as px
import vectorbt as vbt

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

    def vbt_init(self):
        vbt_func = vbt.Portfolio.from_signals(init_cash=self.capital, sl_stop=self.SL_pct, tp_stop=self.TP_pct, close=self.backtest_df[CLOSE], entries=self.backtest_df[ENTRY_LONG], exits=self.backtest_df[EXIT_SHORT], short_entries=self.backtest_df[ENTRY_SHORT], short_exits=self.backtest_df[EXIT_SHORT], direction='both', accumulate=False, freq='d')
        vbt_func.plot().show()
        position_df = pd.DataFrame({DATETIME:vbt_func.asset_flow().index, POSITION:vbt_func.asset_flow().values})
        position_fig = px.line(position_df, x=DATETIME, y=POSITION)
        position_fig.show()

        stats_df = vbt_func.stats()
        asset_return = vbt_func.asset_returns()
        asset_value = vbt_func.asset_value()
        cumulative_returns = vbt_func.cumulative_returns()
        return vbt_func, stats_df, asset_return, asset_value, cumulative_returns, position_df
    
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
    
    def generate_backtest_result(self):
        vbt_func, stats_df, asset_return, asset_value, cumulative_returns, position_df = self.vbt_init()
        self.vbt_result(self._strategy_class, self._strategy_config, stats_df, position_df, self.backtest_df, vbt_func, asset_return, asset_value, cumulative_returns)
              



