import os
import json
import logging
import pandas as pd
import types_enums.base_strategy_enum as base_strategy_enum
from types_enums.vbt_enum import *
import plotly.express as px
import vectorbt as vbt
from vectorbt.utils.colors import adjust_opacity

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

    def run_backtest(self, backtest_df):
        self.logger.info(f'Running Backtest - [{self._strategy_class=}, {self._strategy_config=}].')
        self.backtest_execution(backtest_df)

    def backtest_execution(self, backtest_df):
        pf_analyzer = vbt.Portfolio.from_signals(
            init_cash=self.capital, 
            sl_stop=self.SL_pct, 
            tp_stop=self.TP_pct, 
            close=backtest_df[CLOSE], 
            entries=backtest_df[ENTRY_LONG], 
            exits=backtest_df[EXIT_SHORT], 
            short_entries=backtest_df[ENTRY_SHORT], 
            short_exits=backtest_df[EXIT_SHORT], 
            direction='both', # longonly # both
            accumulate=False, 
            freq=self.resample # fix the bug int too big to convert
        )
        

        position_df, stats_df, asset_return_df, asset_value_df, cumulative_returns_df, trade_record_df = self.build_backtest_df(pf_analyzer)
        self.save_backtest_df(self.backtest_df, position_df, stats_df, asset_return_df, asset_value_df, cumulative_returns_df, trade_record_df)
        self.plot_cumulative_return_trades(pf_analyzer)
        self.plot_cumulative_drawdown_return(pf_analyzer)
        
        # self.plot_position(position_df)
        # self.plot_rolling_drawdown(pf_analyzer)
        # self.plot_drawdown_underwater(pf_analyzer)
        # self.plot_order_and_size(pf_analyzer)
        
    def get_position_df(self, pf_analyzer):
        return pd.DataFrame({DATETIME:pf_analyzer.asset_flow().index, POSITION:pf_analyzer.asset_flow().values})
    
    def get_stats_df(self, pf_analyzer):
        return pf_analyzer.stats()

    def get_asset_return_df(self, pf_analyzer):
        return pf_analyzer.asset_returns()

    def get_asset_value_df(self, pf_analyzer):
        return pf_analyzer.asset_value()
    
    def get_cumulative_returns_df(self, pf_analyzer):
        return pf_analyzer.cumulative_returns()

    def get_trade_record_df(self, pf_analyzer):
        return pf_analyzer.positions.records_readable
        
    def build_backtest_df(self, pf_analyzer):
        position_df = self.get_position_df(pf_analyzer)
        stats_df = self.get_stats_df(pf_analyzer)
        asset_return_df = self.get_asset_return_df(pf_analyzer)
        asset_value_df = self.get_asset_value_df(pf_analyzer)
        cumulative_returns_df = self.get_cumulative_returns_df(pf_analyzer)
        trade_record_df = self.get_trade_record_df(pf_analyzer)
        return position_df, stats_df, asset_return_df, asset_value_df, cumulative_returns_df, trade_record_df
    
    def save_backtest_df(
            self, 
            backtest_df: pd.DataFrame,
            position_df: pd.DataFrame,
            stats_df: pd.DataFrame,
            asset_return_df: pd.DataFrame,
            asset_value_df: pd.DataFrame,
            cumulative_returns_df: pd.DataFrame,   
            trade_record_df: pd.DataFrame,
        ):
        save_dir = f'{os.path.dirname(__file__)}/../backtest_result/{self._strategy_class}/{self._strategy_config}'
        os.makedirs(save_dir, exist_ok=True)
        position_df.to_csv(f'{save_dir}/{self._strategy_config}_position_vbt.csv')
        stats_df.to_csv(f'{save_dir}/{self._strategy_config}_stats_vbt.csv')
        asset_return_df.to_csv(f'{save_dir}/{self._strategy_config}_asset_return_vbt.csv')
        asset_value_df.to_csv(f'{save_dir}/{self._strategy_config}_asset_value_vbt.csv')
        cumulative_returns_df.to_csv(f'{save_dir}/{self._strategy_config}_cumulative_returns_vbt.csv')
        trade_record_df.to_csv(f'{save_dir}/{self._strategy_config}_trade_pnl_vbt.csv')
        backtest_df.to_csv(f'{save_dir}/{self._strategy_config}_metric_df_vbt.csv')
        print('Backtest Results')
        print('---------')
        print(stats_df)
        print('---------')
        print(f'Backtest Report in {self._strategy_config}/{self._strategy_config} Saved Success!')

    def plot_cumulative_return_trades(self, pf_analyzer):
        pf_analyzer.plot().show()
        # vbt.plot(pf_analyzer)
    
    def plot_cumulative_drawdown_return(self, pf_analyzer):
        pf_analyzer.qs.plot_snapshot()
    
    # TODO FIX: plot got squeezed
    def plot_position(self, position_df):
        position_fig = px.line(position_df, x=DATETIME, y=POSITION)
        position_fig.show()        
    
    # TODO FIX: This object already contains one column of data
    def plot_drawdown_underwater(self, pf_analyzer):
        pf_analyzer.plot(
            subplots=['drawdowns', 'underwater'],
            column=10,
            subplot_settings=dict(
                drawdowns=dict(top_n=3),
                underwater=dict(
                    trace_kwargs=dict(
                        line=dict(color='#FF6F00'),
                        fillcolor=adjust_opacity('#FF6F00', 0.3)
                    )
                )
            )
        )

    # TODO FIX: This object already contains one column of data
    def plot_order_and_size(self, pf_analyzer):
        order_size = pf_analyzer.orders.size.to_pd(fill_value=0.)
        fig = pf_analyzer.plot(subplots=[
            'orders',
            ('order_size', dict(
                title='Order Size',
                yaxis_kwargs=dict(title='Order size'),
                check_is_not_grouped=True
            ))  # placeholder
        ], column=10)
        order_size[10].rename('Order Size').vbt.barplot(
            add_trace_kwargs=dict(row=2, col=1),
            fig=fig
        )
    
    # TODO FIX: This object already contains one column of data
    def plot_rolling_drawdown(self, pf_analyzer):
        subplots = [
            ('cumulative_returns', dict(
                title='Cumulative Returns',
                yaxis_kwargs=dict(title='Cumulative returns'),
                plot_func='returns.vbt.returns.cumulative.vbt.plot',
                pass_add_trace_kwargs=True
            )),
            ('rolling_drawdown', dict(
                title='Rolling Drawdown',
                yaxis_kwargs=dict(title='Rolling drawdown'),
                plot_func=[
                    'returns.vbt.returns',  # returns accessor
                    (
                        'rolling_max_drawdown',  # function name
                        (vbt.Rep('window'),)),  # positional arguments
                    'vbt.plot'  # plotting function
                ],
                pass_add_trace_kwargs=True,
                trace_names=[vbt.Sub('rolling_drawdown(${window})')],  # add window to the trace name
            ))
        ]
        pf_analyzer.plot(
            subplots,
            column=10,
            subplot_settings=dict(
                rolling_drawdown=dict(
                    template_mapping=dict(
                        window=10
                    )
                )
            )
        )
        pf_analyzer.plot(subplots, column=10, template_mapping=dict(window=10))

    
              



