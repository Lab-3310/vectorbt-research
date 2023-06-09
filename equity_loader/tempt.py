import os
import sys
from pathlib import Path

sys.path.insert(1, os.path.dirname(__file__) + '/../..')
user_home_path = str(Path.home())

import time
from datetime import datetime
import shioaji as sj
import pandas as pd
import numpy as np

import argparse
import configparser
from utility.csv_dealer import CsvDealer

SINCE = datetime(2018, 12, 7).strftime('%Y-%m-%d')
TO = datetime.now().strftime('%Y-%m-%d') 

# confident config
confident_config = configparser.ConfigParser()
confident_config.read(f'{user_home_path}/backtest-system-tweq/config/confidential.ini')
person_id = confident_config['IdPwd']['person_id']
passwd = confident_config['IdPwd']['passwd']
# ca_path = confident_config['SINO']['ca_path']

# backtest path config
backtest_config = configparser.ConfigParser()
backtest_config.read(f'{user_home_path}/backtest-system-tweq/config/backtest_config.ini')

def tweq_loader():

    parser = argparse.ArgumentParser(description='tuning return plot')
    parser.add_argument('--save_local', help="save_local", default=False)
    parser.add_argument('--save_cloud', help="save_cloud", default=False)

    args = parser.parse_args()
    save_local = args.save_local
    save_cloud = args.save_cloud

    if save_local:
        tweq_loading_path = backtest_config['paths']['local_tweq_path']
        print('--------------------------------------------')
        print('TWEQ saving in local DB:' + tweq_loading_path)
        print('--------------------------------------------')
    elif save_cloud:
        tweq_loading_path = backtest_config['paths']['drive_tweq_path']
        print('--------------------------------------------')
        print('TWEQ saving in Drive:' + tweq_loading_path)
        print('--------------------------------------------')

    timeframe = '1m'
    product_type = 'equity'
    date_path = tweq_loading_path + '/equity/'
    directory = date_path + '/minute'
    os.makedirs(directory, exist_ok=True)

    path = tweq_loading_path + '/tweq'
    os.makedirs(path, exist_ok=True)
    # login
    api = sj.Shioaji()
    api.login(
        person_id=person_id,
        passwd=passwd,
        contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done.")
    )
    time.sleep(10)

    # loading
    stock_contract_list = np.sort(
        [x['code'] for x in list(api.Contracts.Stocks['TSE']) + list(api.Contracts.Stocks['OTC']) if
        (sum(c.isdigit() for c in x['code']) == 4) & (len(x['code']) == 4) &
        (x['category'] != '00') & (x['category'] != '')])
    for stock in stock_contract_list:
        time.sleep(0.1)
        print(f'process stock {stock}')
        file = f'{directory}/{stock}_{product_type}_{timeframe}.csv'
        if os.path.isfile(file):
            FORMAT = '%Y-%m-%d %H:%M:%S'
            csv_writer = CsvDealer(file, None, None, FORMAT)
            start_dt = csv_writer.get_last_row_date_csv(format=FORMAT)
            start_day_dt = start_dt.strftime('%Y-%m-%d')
            kbars = api.kbars(api.Contracts.Stocks[stock], start=start_day_dt, end=TO)
            df = pd.DataFrame({**kbars})
            df.ts = pd.to_datetime(df.ts)
            df = df.rename({'ts':'datetime', 'Open':'open', 'Close':'close', 'High':'high', 'Low':'low', 'Volume':'volume'}, axis=1)
            df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
            for row in df.iterrows():
                row=row[1]
                csv_writer.write_if_needed([row[0], row[1], row[2], row[3], row[4], row[5]], start_dt)
        else:
            kbars = api.kbars(api.Contracts.Stocks[stock], start=SINCE, end=TO, timeout=300000)
            df = pd.DataFrame({**kbars})
            df.ts = pd.to_datetime(df.ts)
            df = df.rename({'ts':'datetime', 'Open':'open', 'Close':'close', 'High':'high', 'Low':'low', 'Volume':'volume'}, axis=1)
            df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
            df.to_csv(file, index=False)
 
if __name__ == '__main__':
    tweq_loader()

