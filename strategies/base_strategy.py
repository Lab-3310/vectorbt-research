import os
import json
import time
import datetime
import pandas as pd

import types_enums.base_strategy_enum as base_strategy_enum

class BaseStrategy:
    def __init__(self, strategy_class: str, strategy_config: str):
        self._strategy_class = strategy_class
        self._strategy_config = strategy_config
        
        with open(f'{os.path.dirname(__file__)}/../strategies_config/{strategy_class}/{strategy_config}.json') as f:
            config = json.loads(f.read())
        self._config = config

        # Common configurations
        self._common_config_dict = None
        # Specific configurations
        self._specific_config_dict = {}

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
    def use_spot(self):
        return bool(self._config.get(base_strategy_enum.USE_SPOT, None))
    
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


