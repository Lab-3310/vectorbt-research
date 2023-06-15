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
import argparse
import configparser

from base_loader import SinoBroker
from types_enums.sino_enum import *


class SinoLoader:
    def __init__(self):
        confidential_config = configparser.ConfigParser()
        confidential_config.read(f'{os.path.dirname(__file__)}/../config_confidential/personal_confidential.ini')
        path_config = configparser.ConfigParser()
        path_config.read(f'{os.path.dirname(__file__)}/../config_confidential/personal_confidential.ini')
        self.person_id = confidential_config.get(f'{SinoBroker.SINO}', f'{SinoBroker.PERSON_ID}')
        self.person_wd = confidential_config.get(f'{SinoBroker.SINO}', f'{SinoBroker.PASSWD}')
        self.path_future = path_config.get(f'{SinoBroker.SINO}', f'{SinoBroker.FUTURE}')
        self.path_tweq = path_config.get(f'{SinoBroker.SINO}', f'{SinoBroker.TWEQ}')
        
    def get_future_df(self):
        pass

    def get_tweq_df(self):
        pass

        