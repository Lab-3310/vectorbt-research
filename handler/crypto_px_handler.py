import os, sys

import pandas as pd
import configparser

from handler.backtest_handler import resample_data

def get_crypto_dir():

    path_config = configparser.ConfigParser()
    path_config.read(f'{os.path.dirname(__file__)}/../config/path_config.ini')
    spot_path = spot_path.get('crypto', 'binance_spot')
    uperp_path = uperp_path.get('crypto', 'binance_uperp')

    return spot_path, uperp_path

def get_crypto_data_df(symbol, spot_path=None, uperp_path=None, is_spot=False, is_uperp=False, resample_p=False):

    if is_spot:
        min_data = pd.read_csv(spot_path + f'/{symbol}_1m.csv', index_col='datetime')
    elif is_uperp:
        min_data = pd.read_csv(uperp_path + f'/{symbol}_1m.csv', index_col='datetime')

    min_data.index = pd.to_datetime(min_data.index, format='%Y-%m-%d %H:%M:%S')
    data_df = resample_data(min_data, resample_p)

    return data_df
