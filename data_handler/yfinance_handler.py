import yfinance as yf
import os
from types_enums.yfinance_enum import yf_pool as pool

import configparser
import platform
import pandas as pd

class YFinanceHandler:
    """
    A class for handling Yahoo Finance daily data retrieval and processing.

    Attributes:
        pool (list): List of stock symbols to retrieve data for.
    """

    def __init__(self, pool=pool):
        """
        Initialize a YFinanceHandler instance.

        Args:
            pool (list, optional): List of stock symbols to retrieve data for.
                Defaults to the pool defined in ticker.py.
        """
        self.pool = pool
        print('yfinance handler init')

    def handler_download(self):
        """
        solve path problem in the func "save_ohlcv_dict_to_df()"
        """
        # os.makedirs(f'{os.path.dirname(__file__)}/../database/YFIN', exist_ok=True) 
        # #TODO why in finlab, binance is /../..??, need to switch to general path 
        self.save_ohlcv_dict_to_df()

    def get_yf_result(self):
        """
        Retrieve historical OHLC (Open, High, Low, Close) yf result for the specified pool of symbols.

        Returns:
            pandas.DataFrame: DataFrame containing historical OHLC data.
        """
        result = yf.download(self.pool, ignore_tz=True)
        adj_rate = result['Adj Close'] / result['Close']
        result['Close'] *= adj_rate
        result['High'] *= adj_rate
        result['Low'] *= adj_rate
        result['Open'] *= adj_rate
        return result.loc[:, (slice(None), self.pool)]

    def get_ohlcv_dict(self):
        """
        Process historical Open, High, Low, Close, and Volume (OHLCV) data into a structured format.

        This function takes a DataFrame containing historical OHLCV data and returns a dictionary containing
        various processed data points related to financial market OHLCV information.

        Args:
            yf_result (pandas.DataFrame): DataFrame containing historical OHLCV data.

        Returns:
            dict: A dictionary containing the following processed data:
                - 'close': Closing prices.
                - 'high': High prices.
                - 'low': Low prices.
                - 'open': Opening prices.
                - 'volume': Volume of trades.
                - 'returns': Daily returns based on closing prices.
                - 'dv': Dollar volume (closing price multiplied by volume).
                - 'vwap': Volume-weighted average price.
                - 'cap': Market capitalization (closing price multiplied by volume).

        Raises:
            ValueError: If the input DataFrame is missing any of the required columns ('Open', 'High', 'Low', 'Close', 'Volume').
        """
        yf_result = self.get_yf_result()
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in yf_result.columns]
        
        if missing_columns:
            raise ValueError(f"Input DataFrame is missing the following columns: {', '.join(missing_columns)}")
        
        ohlcv_dict = {
            'close': yf_result['Close'],
            'high': yf_result['High'],
            'low': yf_result['Low'],
            'open': yf_result['Open'],
            'volume': yf_result['Volume'],
            'returns': (yf_result['Close']/yf_result['Close'].shift(1)) - 1, # TODO just check
            'dv': yf_result['Close'] * yf_result['Volume'],
            'vwap': (yf_result['Close'] + yf_result['Open'] + yf_result['High'] + yf_result['Low']) / 4,
            'cap': yf_result['Close'] * yf_result['Volume'] # TODO: fix cap calculation
        }
        return ohlcv_dict

    def get_exp_returns(self):
        """
        Calculate expected returns based on historical OHLC data.

        This function calculates expected returns using historical OHLC data and specifically utilizes the 'Open' column
        from the 'yf_result' DataFrame obtained via the 'get_yf_result' method. The returns are based on a two-day time
        difference.

        Returns:
            exp_returns (pd.Series): Series containing expected returns calculated from the 'Open' prices with a two-day time difference.
        
        """
        yf_result = self.get_yf_result()
        exp_returns = yf_result['Open'].pct_change().shift(-2) #TODO: Why?
        return exp_returns
    
    def save_ohlcv_dict_to_df(self):
        ohlcv_dict = self.get_ohlcv_dict()

        config_path = os.path.expanduser('~/vectorbt-research/config/config.ini')
        download_config = configparser.ConfigParser()
        download_config.read(config_path) # Load the config.ini file
        if platform.system() == "Darwin": # Retrieve the value based on the platform
            yfinance_path = download_config.get('path', 'mac_path')
        elif platform.system() == "Windows":
            yfinance_path = download_config.get('path', 'window_path')
        
        # create the database path file you designated
        data_path = yfinance_path + f'/YFIN'
        os.makedirs(data_path,  exist_ok=True)


        for key, df in ohlcv_dict.items():
            file_name = f'{key}.csv'  # Constructing the file name based on the key
            file_path = os.path.join(data_path, file_name)
            df.to_csv(file_path)
        print('yfinance data saved')


