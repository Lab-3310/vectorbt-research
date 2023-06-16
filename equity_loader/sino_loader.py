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
import configparser
from enum import Enum
from datetime import datetime

from equity_loader.base_loader import SinoBroker
from types_enums.sino_enum import *
from equity_loader.equity_list import FUTURE_TICKER
from equity_loader.csv_handler import CsvHandler

class SinoLoader:
    def __init__(self):
        confidential_config = configparser.ConfigParser()
        confidential_config.read(f'{os.path.dirname(__file__)}/../config_confidential/personal_confidential.ini')
        path_config = configparser.ConfigParser()
        path_config.read(f'{os.path.dirname(__file__)}/../config/path_config.ini')
        self.person_id = confidential_config.get(f'{SinoBroker.SINO.value}', f'{SinoBroker.PERSON_ID.value}')
        self.pass_wd = confidential_config.get(f'{SinoBroker.SINO.value}', f'{SinoBroker.PASSWORD.value}')
        self.path_future = path_config.get(f'{SinoBroker.SINO.value}', f'{SinoBroker.FUTURE.value}')
        self.path_tweq = path_config.get(f'{SinoBroker.SINO.value}', f'{SinoBroker.TWEQ.value}')
        self.api = sj.Shioaji()
        self.api.login(
            person_id=self.person_id,
            passwd=self.pass_wd,
            contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done.")
        ) 
        self.FUTURE_SINCE = datetime(2020, 3, 23).strftime('%Y-%m-%d')
        self.TO = datetime.now().strftime('%Y-%m-%d') 
        
    def get_future_df(self):
        for symbol in FUTURE_TICKER:
            time.sleep(10)
            directory = self.path_future
            os.makedirs(directory, exist_ok=True)
            print(f'Loading {symbol}...')
            file = f'{directory}/{symbol}_future_1m.csv'
            if os.path.isfile(file):
                FORMAT = '%Y-%m-%d %H:%M:%S'
                csv_writer = CsvHandler(file, None, None, FORMAT)
                start_dt = csv_writer.get_last_row_date_csv(format=FORMAT)
                start_day_dt = start_dt.strftime('%Y-%m-%d')
                kbars = self.api.kbars(self.api.Contracts.Futures[symbol], start=start_day_dt, end=TO)
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

    def get_tweq_df(self):
        pass

        