import talib as ta
import os, sys
from pathlib import Path
import json 

sys.path.insert(1, os.path.dirname(__file__) + '/../..')
user_home_path = str(Path.home())

import argparse
import configparser
import numpy as np
import pandas as pd
import vectorbt as vbt
from datetime import datetime
import plotly.express as px

import warnings
warnings.filterwarnings("ignore")

from dealer.px_handler import *
from dealer.configparser_dealer import *
from backtest_engine.vbt_support import *

"""
--strategy_logic ExampleStrategy  --strategy_config ERZ_ETH_30m_b03 --time_code all
--strategy_logic ExampleStrategy  --strategy_config ERZ_ETH_30m_b02 --time_code all

"""

def ExampleStrategy():

    today_date = datetime.today().strftime('%Y-%m-%d')

    parser = argparse.ArgumentParser(description='strategy backtest')
    parser.add_argument('--time_code', help="time code", required=True)
    parser.add_argument('--strategy_logic', help="strategy logic", required=True)
    parser.add_argument('--strategy_config', help="strategy config", required=True)
    # default
    parser.add_argument('--start_date', help="bt start", required=False)
    parser.add_argument('--end_date', help="bt end", required=False)
    parser.add_argument('--optimize', help="run optimize", required=False, default=False)
    parser.add_argument('--end_bar_time', help="end_bar_time", required=False, default=False)
    
    args = parser.parse_args()
    strategy_logic = args.strategy_logic
    strategy_config = args.strategy_config
    time_code = args.time_code
    start_date = args.start_date
    end_date = args.end_date
    optimize = args.optimize

    with open(f'{user_home_path}/backtest-engine-alpha/backtest_engine/strategies_parameters/{strategy_logic}/{strategy_config}.json') as f:
        config = json.loads(f.read())   
    # strategy infos
    strategy_capital = config['account_info']['capital']
    designer = config['strategy_details']['designer']
    design_date = config['strategy_details']['design_date']
    status = config['strategy_details']['status']
    asset_class = config['asset_info']['asset_class']
    exchange = config['exchange']
    symbol = config['symbol']
    resample_p = config['prepare_data_param']['resample']
    short_code = config['short_code']

    # params
    er_p = config['prepare_data_param']['er_p']

    # tpsl
    sl_pct = config['trading_data_param']['SL_pct']
    tp_ratio = config['trading_data_param']['TP_ratio']
    tp_pct = sl_pct * tp_ratio
    
    if asset_class == 'CRYPTO':
       data_df = px_handler(symbol, resample_p, asset_class, exchange)
    elif asset_class == 'FX':
        if exchange == 'META':
            data_df = px_handler(symbol, resample_p, asset_class, exchange)
    else:
        raise(ValueError('Data Import Sth Wrong!!'))

    # slice 
    bt_df = bar_slicer(time_code, data_df, today_date, start_date, end_date)

    # prepare data step
    bt_df["price_delta"] = (bt_df["close"] - bt_df["close"].shift(1))
    bt_df["total_price_delta"] = (bt_df["close"] - bt_df["close"].shift(er_p))
    bt_df["delta_abs_sum"] = ta.SUM(bt_df["price_delta"].abs(), timeperiod=er_p)

    bt_df["efficiency_ratio"] = bt_df["total_price_delta"]/bt_df["delta_abs_sum"]
    bt_df["prev_efficiency_ratio"] = bt_df["efficiency_ratio"].shift(1)

    # zscore
    bt_df["efficiency_ratio_avg"] = ta.SMA(bt_df["efficiency_ratio"], timeperiod=er_p)
    bt_df["efficiency_ratio_stddev"] = ta.STDDEV(bt_df["efficiency_ratio"], timeperiod=er_p)
    bt_df["efficiency_ratio_zscore"] = (bt_df["prev_efficiency_ratio"] - bt_df["efficiency_ratio_avg"])/bt_df["efficiency_ratio_stddev"]
    bt_df["prev_efficiency_ratio_zscore"] = bt_df["efficiency_ratio_zscore"].shift(1)

    # logic
    CrossUp_00 = (bt_df['efficiency_ratio_zscore'] >= 0.0) & (bt_df['prev_efficiency_ratio_zscore'] < 0.0)
    CrossUp_01 = (bt_df['efficiency_ratio_zscore'] >= 1.0) & (bt_df['prev_efficiency_ratio_zscore'] < 1.0)
    CrossUp_02 = (bt_df['efficiency_ratio_zscore'] >= 2.0) & (bt_df['prev_efficiency_ratio_zscore'] < 2.0)
    CrossUp_03 = (bt_df['efficiency_ratio_zscore'] >= 3.0) & (bt_df['prev_efficiency_ratio_zscore'] < 3.0)

    CrossDown_00 = (bt_df['efficiency_ratio_zscore'] <= 0.0) & (bt_df['prev_efficiency_ratio_zscore'] > 0.0)
    CrossDown_n01 = (bt_df['efficiency_ratio_zscore'] <= -1.0) & (bt_df['prev_efficiency_ratio_zscore'] > -1.0)
    CrossDown_n02 = (bt_df['efficiency_ratio_zscore'] <= -2.0) & (bt_df['prev_efficiency_ratio_zscore'] > -2.0)
    CrossDown_n03 = (bt_df['efficiency_ratio_zscore'] <= -3.0) & (bt_df['prev_efficiency_ratio_zscore'] > -3.0)    

    bt_df['entry_long'] = np.where(CrossUp_01,True, False)
    bt_df['entry_short'] = np.where(CrossDown_n01 ,True, False)

    bt_df['exit_long'] = np.where(CrossUp_03 | CrossDown_00,True, False)
    bt_df['exit_short'] = np.where(CrossDown_n03 | CrossUp_00,True, False) 


    # run backtest
    pf = vbt.Portfolio.from_signals(
    init_cash=strategy_capital,
    sl_stop = sl_pct,
    tp_stop = tp_pct,
    close = bt_df['close'],
    entries = bt_df['entry_long'],
    exits = bt_df['exit_short'],
    short_entries = bt_df['entry_short'],
    short_exits = bt_df['exit_short'],
    direction = 'both',
    accumulate = False,
    freq = 'd' # this will change either II use what resample_p
    )
    vbt_report = pf.plot()

    # position
    position = pf.asset_flow()
    position_df = pd.DataFrame({'datetime':position.index, 'position':position.values})
    # plot position
    positionfig = px.line(position_df, x='datetime', y="position")
    positionfig.show()

    # printing 
    print("---------")
    print(f"Running {short_code} trading {asset_class} on {exchange} in {symbol} {resample_p}")
    print("Stats")
    print("---------")
    vbt_report.show()
    stats_df = pf.stats()
    print(stats_df)
    print("---------")
    print("strategy metric df")
    print(bt_df.tail(5))
    print("---------")
    asset_return = pf.asset_returns()
    asset_value  = pf.asset_value()
    cumulative_returns = pf.cumulative_returns()
    save_dir = f'{user_home_path}/backtest-engine-alpha/data_center/vector_bt'

    vbt_saver_printer(user_home_path, save_dir, strategy_logic, strategy_config, stats_df, position_df, bt_df, pf, asset_return, asset_value, cumulative_returns, designer, design_date, status)

if __name__ == '__main__':
    ExampleStrategy()

