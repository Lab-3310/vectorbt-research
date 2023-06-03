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

def datetime_slicer(time_code, data_df, today_date, start_date: None, end_date: None):
    
    if time_code == 'all':
        selected_data_df = data_df.loc[:today_date]
    elif time_code == 'select':
        selected_data_df = data_df.loc[f'{start_date} 18:30:00':f'{end_date} 18:30:00']
    # year
    elif time_code == '2020':
        selected_data_df = data_df.loc['2020-01-01 18:30:00':'2021-01-01 18:30:00']
    elif time_code == '2021':
        selected_data_df = data_df.loc['2021-01-01 18:30:00':'2022-01-01 18:30:00']
    elif time_code == '2022':
        selected_data_df = data_df.loc['2022-01-01 18:30:00':f'{today_date} 18:30:00']
    # half year
    elif time_code == '1H20':
        selected_data_df = data_df.loc['2020-01-01 18:30:00':'2020-07-01 18:30:00']
    elif time_code == '2H20':
        selected_data_df = data_df.loc['2020-07-01 18:30:00':'2021-01-01 18:30:00']
    elif time_code == '1H21':
        selected_data_df = data_df.loc['2021-01-01 18:30:00':'2021-07-01 18:30:00']
    elif time_code == '2H21':
        selected_data_df = data_df.loc['2021-07-01 18:30:00':'2022-01-01 18:30:00']
    elif time_code == '1H22':
        selected_data_df = data_df.loc['2022-01-01 18:30:00':'2022-07-01 18:30:00']
    elif time_code == '2H22':
        selected_data_df = data_df.loc['2022-07-01 18:30:00':'2023-01-01 18:30:00']
    elif time_code == '1H23':
        selected_data_df = data_df.loc['2023-01-01 18:30:00':'2023-07-01 18:30:00']
    elif time_code == '2H23':
        selected_data_df = data_df.loc['2023-07-01 18:30:00':'2024-01-01 18:30:00']
    # quarter
    elif time_code == '1Q20':
        selected_data_df = data_df.loc['2020-01-01 18:30:00':'2020-04-01 18:30:00']
    elif time_code == '2Q20':
        selected_data_df = data_df.loc['2020-04-01 18:30:00':'2020-07-01 18:30:00']
    elif time_code == '3Q20':
        selected_data_df = data_df.loc['2020-07-01 18:30:00':'2020-10-01 18:30:00']
    elif time_code == '4Q20':
        selected_data_df = data_df.loc['2020-10-01 18:30:00':'2021-01-01 18:30:00']
    elif time_code == '1Q21':
        selected_data_df = data_df.loc['2021-01-01 18:30:00':'2021-04-01 18:30:00']
    elif time_code == '2Q21':
        selected_data_df = data_df.loc['2021-04-01 18:30:00':'2021-07-01 18:30:00']
    elif time_code == '3Q21':
        selected_data_df = data_df.loc['2021-07-01 18:30:00':'2021-10-01 18:30:00']
    elif time_code == '4Q21':
        selected_data_df = data_df.loc['2021-10-01 18:30:00':'2022-01-01 18:30:00']
    elif time_code == '1Q22':
        selected_data_df = data_df.loc['2022-01-01 18:30:00':'2022-04-01 18:30:00']
    elif time_code == '2Q22':
        selected_data_df = data_df.loc['2022-04-01 18:30:00':'2022-07-01 18:30:00']
    elif time_code == '3Q22':
        selected_data_df = data_df.loc['2022-07-01 18:30:00':f'2022-10-01 18:30:00']
    elif time_code == '4Q22':
        selected_data_df = data_df.loc['2022-10-01 18:30:00':f'2023-01-01 18:30:00'] 
    elif time_code == '1Q23':
        selected_data_df = data_df.loc['2023-01-01 18:30:00':f'2023-04-01 18:30:00'] 
    elif time_code == '2Q23':
        selected_data_df = data_df.loc['2023-04-01 18:30:00':f'2023-07-01 18:30:00'] 
    elif time_code == '3Q23':
        selected_data_df = data_df.loc['2023-07-01 18:30:00':f'2023-10-01 18:30:00'] 
    elif time_code == '4Q23':
        selected_data_df = data_df.loc['2023-10-01 18:30:00':f'2024-01-01 18:30:00'] 
   
    # for special request
    elif time_code == 'R1M':
        selected_data_df = data_df.loc['2022-10-01 18:30:00':f'{today_date} 18:30:00']
    elif time_code == 'R3M':
        selected_data_df = data_df.loc['2022-09-01 18:30:00':f'{today_date} 18:30:00']
    else:
        raise ValueError('Wrong Period!')
    
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