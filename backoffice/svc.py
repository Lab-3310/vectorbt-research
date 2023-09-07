



def ohlcv_resample(df_ohlcv, freq):
    df = df_ohlcv.copy()
    df['open'] = df['open'].resample(freq).first()
    df['high'] = df['high'].resample(freq).max()
    df['low'] = df['low'].resample(freq).min()
    df['close'] = df['close'].resample(freq).last()
    df['volume'] = df['volume'].resample(freq).sum()
    df.dropna(inplace=True)
    return df