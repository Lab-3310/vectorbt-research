import pandas as pd
from datetime import datetime, timedelta

from types_enums.data_enum import *

def resample_data(min_data, resample_p, end_bar_time=False):
    data_df = pd.DataFrame()
    for col in min_data.columns:
        if 'open' in col:
            data_df[col] = min_data[col].resample(resample_p, origin='epoch').first()
        if 'high' in min_data.columns:
            data_df['high'] = min_data['high'].resample(resample_p, origin='epoch').max()
        if 'low' in min_data.columns:
            data_df['low'] = min_data['low'].resample(resample_p, origin='epoch').min()
        if 'close' in col:
            data_df[col] = min_data[col].resample(resample_p, origin='epoch').last()
        if 'volume' in min_data.columns:
            data_df['volume'] = min_data['volume'].resample(resample_p, origin='epoch').sum()
    if end_bar_time:
        data_df = data_df.shift(1)
    data_df = data_df.dropna()

    return data_df

def datetime_slicer(backtest_time, data_df, start_date=None, end_date=None, count_to_now=True):
    backtest_time_mapping = {
        'all': slice(None, datetime.now()),
        'select': slice(None, datetime.now()),
        '2020': slice('2020-01-01 18:30:00', '2021-01-01 18:30:00'),
        '2021': slice('2021-01-01 18:30:00', '2022-01-01 18:30:00'),
        '2022': slice('2022-01-01 18:30:00', '2023-01-01 18:30:00'),
        '2023': slice('2023-01-01 18:30:00', '2024-01-01 18:30:00'),
        # Add more mappings for other time codes
    }
    
    if backtest_time in backtest_time_mapping:
        selected_data_df = data_df.loc[backtest_time_mapping[backtest_time]]
    else:
        raise ValueError('backtest_time is not defined!')

    if count_to_now and backtest_time.isdigit():
        year = int(backtest_time)
        cur_year = datetime.now().year
        if cur_year - year >= 3:
            raise ValueError('The backtesting period is too long. It is recommended to start from ' +  f'{cur_year - 2}.')
        
        selected_data_df = data_df.loc[f'{year}-01-01 18:30:00':datetime.now()]

    if backtest_time == 'select':
        date1 = datetime.strptime(start_date, '%Y-%m-%d')
        date2 = datetime.strptime(end_date, '%Y-%m-%d')
        if divmod((date2 - date1).total_seconds(), 31536000)[0] >= 3: # 1 year = 31536000 seconds
            raise ValueError('The backtesting period is too long. The limitation of backtesting period is 3 years')
        
        selected_data_df = data_df.loc[f'{start_date} 18:30:00':f'{end_date} 18:30:00']

    if backtest_time == 'all':
        selected_data_df = data_df

    return selected_data_df

def ohlc_turn_cap(data: pd.DataFrame):
    # for backtesting
    data.rename(columns = {'open':'Open', 'high':'High', 'low':'Low', 'close':'Close', 'volume':'Volume'}, inplace = True)
    return data

def get_timeframe_string(portfolio_df):

    timeframe = portfolio_df.index.to_series().diff()[-1]
    if timeframe == timedelta(minutes=5):
        timeframe_in_string = '5m'
    elif timeframe == timedelta(minutes=15):
        timeframe_in_string = '15m'
    elif timeframe == timedelta(minutes=30):
        timeframe_in_string = '30m'
    elif timeframe == timedelta(hours=1):
        timeframe_in_string = '1h'
    elif timeframe == timedelta(hours=2):
        timeframe_in_string = '2h'
    elif timeframe == timedelta(hours=4):
        timeframe_in_string = '4h'
    elif timeframe == timedelta(hours=8):
        timeframe_in_string = '8h'
    elif timeframe == timedelta(hours=12):
        timeframe_in_string = '12h'
    elif timeframe == timedelta(days=1):
        timeframe_in_string = '1d'
    elif timeframe == timedelta(days=2):
        timeframe_in_string = '2d'
    elif timeframe == timedelta(days=3):
        timeframe_in_string = '3d'

    return timeframe_in_string