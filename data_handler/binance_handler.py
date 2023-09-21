import os, sys
import platform
import time
os.environ['TZ'] = 'Asia/Hong_Kong'

from datetime import datetime, timedelta
import pandas as pd
import csv
import argparse
from argparse import RawTextHelpFormatter
import configparser
import ccxt
from ccxt import ExchangeError
from pathlib import Path

from types_enums.handler_enum import SPOT, UPERP, CPERP, MIN1, HOUR, HOUR4, DAILY, ALL, SELECT

FORMAT = '%Y-%m-%d %H:%M:%S'
SINCE = datetime(2016, 1, 1) # for crypto
TO = datetime.now()


class BinanceHandler:

    def __init__(self):
        pass

    def select_symbol(self):
        select_symbol = [  
            "AAVEUSDT",  
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "ETCUSDT",
            "SOLUSDT",
            "ADAUSDT",
            "LINKUSDT",
            "BCHUSDT",
            "DOTUSDT",
            "LTCUSDT",
            "UNIUSDT",
            "XRPUSDT",
            "XLMUSDT",
            "MATICUSDT"
        ]
        return select_symbol
    
    def handler_download(self): #HINT -> every data handler will have this attribute
        self.binance_handler_init(SPOT, MIN1, SELECT)
        self.binance_handler_init(SPOT, HOUR, SELECT)
        self.binance_handler_init(SPOT, DAILY, SELECT)
        self.binance_handler_init(UPERP, MIN1, SELECT)
        self.binance_handler_init(UPERP, HOUR, SELECT)
        self.binance_handler_init(UPERP, DAILY, SELECT)

    def binance_handler_init(self, product_option: str, timeframe_option: str, symbol_option: str):
        """
        Initialize and configure the Binance data handler for downloading historical cryptocurrency data.

        Args:
            product_option (str): The product option, which can only be one of the following: \n
                - SPOT: Binance SPOT products.
                - UPERP: Binance UPERP products. 
                - CPERP: Binance CPERP products.

            timeframe_option (str): The timeframe option, which can only be one of the following: \n
                - MIN1: 1 minute Kline data.
                - HOUR: 1 hour Kline data.
                - HOUR4: 4 hour Kline data.
                - DAILY: 1 day Kline data.

            symbol_option (str): The symbol option, which can only be one of the following: \n
                - ALL: Fetch data for all available symbols on Binance.
                - SELECT: Fetch data only for a predefined set of symbols.

        """
        valid_product_options = [SPOT, UPERP, CPERP]
        valid_timeframe_options = [MIN1, HOUR, HOUR4, DAILY]
        valid_symbol_options = [ALL, SELECT]

        if product_option not in valid_product_options:
            raise ValueError(f"Invalid product_option. Must be one of {valid_product_options}")

        if timeframe_option not in valid_timeframe_options:
            raise ValueError(f"Invalid timeframe_option. Must be one of {valid_timeframe_options}")

        if symbol_option not in valid_symbol_options:
            raise ValueError(f"Invalid symbol_option. Must be one of {valid_symbol_options}")
        binance_path = f'{os.path.dirname(__file__)}/../database/BINANCE'
        os.makedirs(binance_path, exist_ok=True) #TODO need to switch to general path 

        if product_option == SPOT:
            data_path = binance_path + f'/SPOT/{timeframe_option}'
            client = ccxt.binance()
        elif product_option == UPERP:
            data_path = binance_path + f'/UPERP/{timeframe_option}'
            client = ccxt.binanceusdm()
        elif product_option == CPERP: # FIND SOME SYMBOL ADD IN SELECT
            #TODO check the product_code from binance, curreently mainly use the SPOT and UPERP in USDT
            data_path = binance_path + f'/CPERP/{timeframe_option}'
            client = ccxt.binancecoinm()
        os.makedirs(data_path, exist_ok=True)

        if symbol_option == SELECT:
            for symbol in self.select_symbol():
                print(f'Getting data: {SINCE}, {symbol}, {timeframe_option}')
                self.paginate(client, symbol, timeframe_option, data_path, product_option, SINCE, TO)

        elif symbol_option == ALL:
            # fetch all the availabe symbol on Binance
            symbol_details = client.fetch_markets()
            for i in symbol_details:
                symbol_ = i['symbol']
                symbol_onboard_date = datetime.fromtimestamp(int(i['info']['onboardDate']) / 1000 - 1000)
                start_dt = symbol_onboard_date if symbol_onboard_date > SINCE else SINCE
                print(f'Getting data: {start_dt}, {symbol_}, {timeframe_option}')
                self.paginate(client, symbol_, timeframe_option, data_path, product_option, start_dt, TO)
        else:
            symbol_details = client.fetch_markets()
            symbols = [i['symbol'] for i in symbol_details]
            if symbol in symbols:
                symbol_onboard_date = datetime.fromtimestamp(int(symbol_details[0]['info']['onboardDate']) / 1000 - 1000)
                start_dt = symbol_onboard_date if symbol_onboard_date > SINCE else SINCE
            else:
                start_dt = SINCE
            print(f'Getting data: {start_dt}, {symbol}, {timeframe_option}')
            self.paginate(client, symbol, timeframe_option, data_path, product_option, start_dt, TO)
        print('Saved data.')
    
    def paginate(self, client, symbol, timeframe, directory, type_, start_dt, to_dt=datetime.now()):
        data = []
        file = f'{directory}/{symbol.replace("/", "")}_{type_}_{timeframe}.csv'
        if os.path.isfile(file):
            csv_writer = CsvHandler(file, None, None, FORMAT)
            start_dt = csv_writer.get_last_row_date_csv(format=FORMAT)
        since = self.timestamp_to_int(start_dt)
        while True:
            try:
                patch = client.fetch_ohlcv(symbol, timeframe, since, limit=5000)
                data += patch
                if patch:
                    print(f'[{symbol}] Fetched data from - {patch[0][0]} - {self.timestampt_to_datetime(patch[0][0])} to {self.timestampt_to_datetime(patch[-1][0])}')
                    # update next patch to have since = last ts of patch + 1 millisec to avoid duplication of data
                    since = int(patch[-1][0]) + 1
                    if self.timestampt_to_datetime(since) > to_dt - timedelta(hours=1):
                        break
                    else:
                        time.sleep(client.rateLimit / 1000)
                else:
                    if timeframe == HOUR:
                        since += 2592000000  # 1 month
                    else:
                        since += 60000 * 1000
                        # since += 2592000000  # 1 month
                    print(f'[{symbol}] Trying later start dt - {self.timestampt_to_datetime(since)}')
                    if self.timestampt_to_datetime(since) > datetime.now():
                        break
            except ExchangeError as e:
                print(f'[{symbol}] Getting error {e}')
                break

        print(f'Acquired # of timepoints: {len(data)}')
        if len(data) == 0:
            return

        print(f'First data point: {data[0]}')
        print(f'Last data point: {data[-1]}')

        # last bar is incomplete
        data = data[:-1]
        if os.path.isfile(file):
            for row in data:
                csv_writer.write_if_needed([datetime.fromtimestamp(row[0] / 1000), row[1], row[2], row[3], row[4], row[5]], start_dt)
        else:
            df = pd.DataFrame({
                'datetime': [datetime.fromtimestamp(row[0] / 1000).strftime(FORMAT) for row in data],
                'open': [row[1] for row in data],
                'high': [row[2] for row in data],
                'low': [row[3] for row in data],
                'close': [row[4] for row in data],
                'volume': [row[5] for row in data]
            })

            df.to_csv(file, index=False)
        time.sleep(1)

    def get_start_dt(self, symbols_detail_map, symbol):

        if symbol in symbols_detail_map and 'onboardDate' in symbols_detail_map[symbol]['info']:
            symbol_onboard_date = datetime.fromtimestamp(int(symbols_detail_map[symbol]['info']['onboardDate']) / 1000 - 1000)
            start_dt = symbol_onboard_date if symbol_onboard_date > SINCE else SINCE
        else:
            start_dt = SINCE
        return start_dt

    def timestamp_to_int(self, dt): # takes a datetime object return timestamp in int
        return int(datetime.timestamp(dt) * 1000) 

    def timestampt_to_datetime(self, ts): # takes a timestamp in int return datetime object
        return datetime.fromtimestamp(ts / 1000)

class CsvHandler:

    """
    CsvHandler is a utility class for working with CSV files.

    It provides methods for opening, writing, and closing CSV files, as well as checking and managing file contents.

    Args:
        file_path (str): The path to the CSV file to be managed.
        logger (Logger): An instance of a logger for logging messages and events.
        date_format (str, optional): The date format used in the CSV file. Defaults to '%Y-%m-%d'.
        open_file (bool, optional): Whether to open the file immediately upon initialization. Defaults to True.

    Attributes:
        file_path (str): The path to the CSV file being managed.
        logger (Logger): An instance of a logger for logging messages and events.
        date_format (str): The date format used in the CSV file.
        _file (file object or None): The file object for the CSV file, or None if not open.
        _writer (csv.writer or None): The CSV writer object for writing data to the file, or None if not open.

    Methods:
        open_file(new_file_path=None): Opens the CSV file for writing. Optionally, a new file path can be provided.
        get_last_row_date_csv(format='%Y%m%d'): Retrieves the date from the last row of the CSV file.
        write_to_file(data): Writes data to the CSV file, either as a single string or as a list of values.
        check_open_file(function): Decorator function for checking if the file is open before executing a function.
        write_if_needed(msg, last_update_date): Writes data to the CSV file if it meets certain conditions.
        close(): Closes the CSV file.
        __del__(): Destructor method that automatically closes the CSV file upon object deletion.

    Usage Example:
        # Initialize CsvHandler
        csv_handler = CsvHandler("example.csv", logger, "SampleStrategy")

        # Open the CSV file
        csv_handler.open_file()

        # Write data to the CSV file
        csv_handler.write_to_file("2023-09-17,100.00,101.00,99.50,100.50,10000\n")

        # Close the CSV file
        csv_handler.close()
    """

    def __init__(self, file_path, logger, date_format='%Y-%m-%d', open_file=True):
        self._file_path = file_path
        self.logger = logger
        self._date_format = date_format
        self._file = open(self._file_path, 'a', newline='') if open_file else None
        self._writer = csv.writer(self._file) if open_file else None

    @property
    def file_path(self):
        return self._file_path

    def open_file(self, new_file_path=None):
        if new_file_path is not None:
            self._file_path = new_file_path
        self._file = open(self._file_path, 'a', newline='')
        self._writer = csv.writer(self._file)

    def get_last_row_date_csv(self, format='%Y%m%d'):
        try:
            with open(self._file_path, "r", encoding="utf-8", errors="ignore") as scraped:
                last_row = None
                reader = csv.reader(scraped, delimiter=',')
                for row in reader:
                    if row:  # avoid blank lines
                        last_row = row
                return datetime.strptime(last_row[0], format) if last_row is not None else None
        except FileNotFoundError:
            None

    def write_to_file(self, data):
        if self._file is None:
            self.logger.info('Writing csv file')
            with open(self._file_path, 'a', newline='') as csvfile:
                # add the csv writer
                if isinstance(data, str):
                    csvfile.write(data)
                else:
                    writer = csv.writer(csvfile)
                    writer.writerow(data)
        else:
            if isinstance(data, str):
                self._file.write(data)
            else:
                self._writer.writerow(data)

    def check_open_file(self, function):
        def wrapper():
            func = function()
            splitted_string = func.split()
            return splitted_string

        return wrapper

    def write_if_needed(self, msg, last_update_date):
        if isinstance(last_update_date, str):
            try:
                last_update_date = datetime.strptime(last_update_date, self._date_format)
            except ValueError:
                self.logger.error(f'Cannot transfer to dt - {last_update_date}')
                # no date is found, so write the data anyway
                last_update_date = None
        if isinstance(msg, str):
            data_dt = datetime.strptime(msg.split(',')[0], self._date_format) if last_update_date is not None else None
            if data_dt is None or last_update_date is None or last_update_date < data_dt:
                self._file.write(msg)
        else:
            # list
            data_dt = msg[0]
            if isinstance(data_dt, str):
                data_dt = datetime.strptime(msg[0], self._date_format) if last_update_date is not None else None
            if data_dt is None or last_update_date is None or last_update_date < data_dt:
                self._writer.writerow(msg)

    def close(self):
        self._file.close()

    def __del__(self):
        self.close()
