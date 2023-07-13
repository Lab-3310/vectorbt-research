
import os
import platform
import time
os.environ['TZ'] = 'Asia/Hong_Kong'

if platform.system() == "Darwin":
    time.tzset() # time zone setting

from datetime import datetime, timedelta

import pandas as pd
from ccxt import ExchangeError

import argparse
import configparser
import ccxt
import sys
from pathlib import Path

sys.path.insert(1, os.path.dirname(__file__) + '/..')
root_path = str(Path.home())

from csv_dealer import CsvDealer
from binance_ccxt.symbol_select import *

FORMAT = '%Y-%m-%d %H:%M:%S'
SINCE = datetime(2016, 1, 1) # for crypto
TO = datetime.now()

def timestamp_to_int(dt): # takes a datetime object return timestamp in int
    return int(datetime.timestamp(dt) * 1000) 

def timestampt_to_datetime(ts): # takes a timestamp in int return datetime object
    return datetime.fromtimestamp(ts / 1000)

def paginate(client, symbol, timeframe, directory, type_, start_dt, to_dt=datetime.now()):
    data = []
    file = f'{directory}/{symbol.replace("/", "")}_{type_}_{timeframe}.csv'
    if os.path.isfile(file):
        csv_writer = CsvDealer(file, None, None, FORMAT)
        start_dt = csv_writer.get_last_row_date_csv(format=FORMAT)
    since = timestamp_to_int(start_dt)
    # paginati
    while True:
        try:
            patch = client.fetch_ohlcv(symbol, timeframe, since, limit=5000)
            data += patch
            if patch:
                print(f'[{symbol}] Fetched data from - {patch[0][0]} - {timestampt_to_datetime(patch[0][0])} to {timestampt_to_datetime(patch[-1][0])}')
                # update next patch to have since = last ts of patch + 1 millisec to avoid duplication of data
                since = int(patch[-1][0]) + 1
                if timestampt_to_datetime(since) > to_dt - timedelta(hours=1):
                    break
                else:
                    time.sleep(client.rateLimit / 1000)
            else:
                if timeframe == '1h':
                    since += 2592000000  # 1 month
                else:
                    since += 60000 * 1000
                    # since += 2592000000  # 1 month
                print(f'[{symbol}] Trying later start dt - {timestampt_to_datetime(since)}')
                if timestampt_to_datetime(since) > datetime.now():
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

def get_start_dt(symbols_detail_map, symbol):

    if symbol in symbols_detail_map and 'onboardDate' in symbols_detail_map[symbol]['info']:
        symbol_onboard_date = datetime.fromtimestamp(int(symbols_detail_map[symbol]['info']['onboardDate']) / 1000 - 1000)
        start_dt = symbol_onboard_date if symbol_onboard_date > SINCE else SINCE
    else:
        start_dt = SINCE
    return start_dt


def binance_loader():
    '''
    --symbol_list select --timeframe 1d --product UPERP
    '''
    sys.path.append(f'{root_path}/vectorbt-research') # Get the path to the config.ini file based on the user's operating system

    config_path = os.path.expanduser('~/vectorbt-research/config/config.ini')
    
    download_config = configparser.ConfigParser()
    download_config.read(config_path) # Load the config.ini file
    
    if platform.system() == "Darwin": # Retrieve the value based on the platform
        binance_download_path = download_config.get('binance', 'mac_path')
    elif platform.system() == "Windows":
        binance_download_path = download_config.get('binance', 'window_path')
    # create the database path file you designated
    os.makedirs(binance_download_path, exist_ok=True)
    parser = argparse.ArgumentParser(description='symbol and timeframe')
    parser.add_argument('--symbol_list', help="symbol")
    parser.add_argument('--timeframe', help="timeframe", default='1m')
    parser.add_argument("--product", required=True, help="SPOT USD COIN.")
    args = parser.parse_args()
    symbol_list = args.symbol_list
    product = args.product
    timeframe = args.timeframe
    if product == 'SPOT':
        data_path = f'{binance_download_path}/BINANCE/SPOT/{timeframe}'
    elif product == 'UPERP':
        data_path = f'{binance_download_path}/BINANCE/UPERP/{timeframe}'
    elif product == 'CPERP':
        data_path = f'{binance_download_path}/BINANCE/CPERP/{timeframe}'
    os.makedirs(data_path, exist_ok=True)
    if product == 'SPOT':
        client = ccxt.binance()
    elif product == 'UPERP':
        client = ccxt.binanceusdm()
    elif product == 'CPERP':
        client = ccxt.binancecoinm()
    if symbol_list == 'all':
        symbol_details = client.fetch_markets()
        for i in symbol_details:
            symbol_ = i['symbol']
            symbol_onboard_date = datetime.fromtimestamp(int(i['info']['onboardDate']) / 1000 - 1000)
            start_dt = symbol_onboard_date if symbol_onboard_date > SINCE else SINCE
            print(f'Getting data: {start_dt}, {symbol_}, {timeframe}')
            paginate(client, symbol_, timeframe, data_path, product, start_dt, TO)
    elif symbol_list == 'select':
        for symbol in select_symbol:
            print(f'Getting data: {SINCE}, {symbol}, {timeframe}')
            paginate(client, symbol, timeframe, data_path, product, SINCE, TO)
    else:
        symbol_details = client.fetch_markets()
        symbols = [i['symbol'] for i in symbol_details]
        if symbol in symbols:
            symbol_onboard_date = datetime.fromtimestamp(int(symbol_details[0]['info']['onboardDate']) / 1000 - 1000)
            start_dt = symbol_onboard_date if symbol_onboard_date > SINCE else SINCE
        else:
            start_dt = SINCE
        print(f'Getting data: {start_dt}, {symbol}, {timeframe}')
        paginate(client, symbol, timeframe, data_path, product, start_dt, TO)
    print('Saved data.')
