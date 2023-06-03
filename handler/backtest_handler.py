import pandas as pd
from datetime import datetime, timedelta

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

def datetime_slicer(time_code, data_df, start_date=None, end_date=None, count_to_now=True):
    
    time_code_mapping = {
        'all': slice(None, datetime.now()),
        'select': slice(f'{start_date} 18:30:00', f'{end_date} 18:30:00'),
        '2020': slice('2020-01-01 18:30:00', '2021-01-01 18:30:00'),
        '2021': slice('2021-01-01 18:30:00', '2022-01-01 18:30:00'),
        '2022': slice('2022-01-01 18:30:00', '2023-01-01 18:30:00'),
        '2023': slice('2023-01-01 18:30:00', '2024-01-01 18:30:00'),
        # Add more mappings for other time codes
    }
    
    if time_code in time_code_mapping:
        selected_data_df = data_df.loc[time_code_mapping[time_code]]
    else:
        raise ValueError('Time Code not defined')
    
    if count_to_now and time_code.isdigit():
        year = int(time_code)
        selected_data_df = selected_data_df.loc[f'{year}-01-01 18:30:00':datetime.now()]
    
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