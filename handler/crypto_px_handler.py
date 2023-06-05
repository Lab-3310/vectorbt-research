import os
import platform
import pandas as pd
import configparser

from handler.backtest_handler import resample_data

def get_crypto_data_df(symbol, use_spot=False, resample_p=False):

    path_config = configparser.ConfigParser()
    path_config.read(f'{os.path.dirname(__file__)}/../config/path_config.ini')

    if use_spot: # for crypto default use_spot as false is using uperp
        spot_path = path_config.get('crypto', 'binance_spot')
        if platform.system() == "Darwin":
            min_data = pd.read_csv(spot_path + f'/{symbol}_1m.csv', index_col='datetime')
        else:
            min_data = pd.read_csv(spot_path + f'\{symbol}_1m.csv', index_col='datetime')
    else:
        uperp_path = path_config.get('crypto', 'binance_uperp')
        if platform.system() == "Darwin":
            min_data = pd.read_csv(uperp_path + f'/{symbol}_1m.csv', index_col='datetime')
        else:
            min_data = pd.read_csv(uperp_path + f'\{symbol}_1m.csv', index_col='datetime')

    min_data.index = pd.to_datetime(min_data.index, format='%Y-%m-%d %H:%M:%S')
    data_df = resample_data(min_data, resample_p)

    return data_df
