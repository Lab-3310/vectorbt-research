import pandas as pd

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