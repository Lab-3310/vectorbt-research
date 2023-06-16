import os, sys
import shioaji as sj

sys.path.insert(1, os.path.dirname(__file__) + '/../..')
os.environ['TZ'] = 'Asia/Hong_Kong'

import platform 
import time
if platform.system() == "Darwin":
    time.tzset() # time zone setting

from datetime import datetime
import pandas as pd
import numpy as np
import configparser
from enum import Enum
from datetime import datetime

from types_enums.sino_enum import *
from equity_loader.equity_list import FUTURE_TICKER
from equity_loader.csv_handler import CsvHandler

'''
Some reference for Sino

https://ithelp.ithome.com.tw/articles/10280898

'''

class SinoBroker(Enum):
    SINO = 'sino'
    TWEQ = 'tweq'
    FUTURE = 'future'
    PERSON_ID = 'person_id'
    PASSWORD = 'pass_wd'

class SinoLoader:
    def __init__(self):
        confidential_config = configparser.ConfigParser()
        confidential_config.read(f'{os.path.dirname(__file__)}/../config_confidential/personal_confidential.ini')
        path_config = configparser.ConfigParser()
        path_config.read(f'{os.path.dirname(__file__)}/../config/path_config.ini')
        self.person_id = confidential_config.get(f'{SinoBroker.SINO.value}', f'{SinoBroker.PERSON_ID.value}')
        self.password = confidential_config.get(f'{SinoBroker.SINO.value}', f'{SinoBroker.PASSWORD.value}')
        self.path_future = path_config.get(f'{SinoBroker.SINO.value}', f'{SinoBroker.FUTURE.value}')
        self.path_tweq = path_config.get(f'{SinoBroker.SINO.value}', f'{SinoBroker.TWEQ.value}')
        self.FUTURE_SINCE = datetime(2020, 3, 23).strftime('%Y-%m-%d')
        self.EQUITY_SINCE = datetime(2018, 12, 7).strftime('%Y-%m-%d')
        self.TO = datetime.now().strftime('%Y-%m-%d') 
        self.api = sj.Shioaji()
    
    def sino_login(self, person_id, password):
        self.api.login(person_id=person_id, passwd=password, contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done."))
        print('SINO Login!') 
        time.sleep(5)
    
    def sino_logout(self):
        self.api.logout()
        print('SINO Logout!')
        time.sleep(5)

    def download_future_df(self):
        self.sino_login(self.person_id, self.password)
        os.makedirs(self.path_future, exist_ok=True)
        for symbol in FUTURE_TICKER:
            print(f'Loading {symbol}...')
            file = f'{self.path_future}/{symbol}_future_1m.csv'
            if os.path.isfile(file):
                FORMAT = '%Y-%m-%d %H:%M:%S'
                csv_writer = CsvHandler(file, None, None, FORMAT)
                start_dt = csv_writer.get_last_row_date_csv(format=FORMAT)
                start_day_dt = start_dt.strftime('%Y-%m-%d')
                kbars = self.api.kbars(self.api.Contracts.Futures[symbol], start=start_day_dt, end=self.TO)
                df = pd.DataFrame({**kbars})
                df.ts = pd.to_datetime(df.ts)
                df = df.rename({'ts':'datetime', 'Open':'open', 'Close':'close', 'High':'high', 'Low':'low', 'Volume':'volume'}, axis=1)
                df = df[['datetime','open','high','low','close','volume']]
                for row in df.iterrows():
                    row=row[1]
                    csv_writer.write_if_needed([row[0], row[1], row[2], row[3], row[4], row[5]], start_dt)
            else:
                kbars = self.api.kbars(self.api.Contracts.Futures[symbol], start=self.FUTURE_SINCE, end=self.TO, timeout=300000)
                df = pd.DataFrame({**kbars})
                df.ts = pd.to_datetime(df.ts)
                df = df.rename({'ts':'datetime','Open':'open', 'Close':'close', 'High':'high', 'Low':'low', 'Volume':'volume'}, axis=1)
                df = df[['datetime','open', 'high', 'low', 'close', 'volume']]
                df.to_csv(file, index=False)
        self.sino_logout

    def get_stock_list(self):
        stock_list = np.sort(
            [x['code'] for x in list(self.api.Contracts.Stocks['TSE']) + list(self.api.Contracts.Stocks['OTC']) if
            (sum(c.isdigit() for c in x['code']) == 4) & (len(x['code']) == 4) &
            (x['category'] != '00') & (x['category'] != '')])
        return stock_list

    def download_tweq_df(self):
        self.sino_login(self.person_id, self.password)
        os.makedirs(self.path_tweq, exist_ok=True)
        stock_list = self.get_stock_list()
        for stock in stock_list:
            time.sleep(0.1)
            print(f'loading stock {stock}')

            file = f'{self.path_tweq}/{stock}_equity_1m.csv'
            if os.path.isfile(file):
                FORMAT = '%Y-%m-%d %H:%M:%S'
                csv_writer = CsvHandler(file, None, None, FORMAT)
                start_dt = csv_writer.get_last_row_date_csv(format=FORMAT)
                start_day_dt = start_dt.strftime('%Y-%m-%d')
                kbars = self.api.kbars(self.api.Contracts.Stocks[stock], start=start_day_dt, end=self.TO)
                df = pd.DataFrame({**kbars})
                df.ts = pd.to_datetime(df.ts)
                df = df.rename({'ts':'datetime', 'Open':'open', 'Close':'close', 'High':'high', 'Low':'low', 'Volume':'volume'}, axis=1)
                df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
                for row in df.iterrows():
                    row=row[1]
                    csv_writer.write_if_needed([row[0], row[1], row[2], row[3], row[4], row[5]], start_dt)
            else:
                kbars = self.api.kbars(self.api.Contracts.Stocks[stock], start=self.EQUITY_SINCE, end=self.TO, timeout=300000)
                df = pd.DataFrame({**kbars})
                df.ts = pd.to_datetime(df.ts)
                df = df.rename({'ts':'datetime', 'Open':'open', 'Close':'close', 'High':'high', 'Low':'low', 'Volume':'volume'}, axis=1)
                df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
                df.to_csv(file, index=False)
        self.sino_logout

        