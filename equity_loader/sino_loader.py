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


class SinoLoader:
    def __init__(self):
        with open(f'{os.path.dirname(__file__)}/../config/token_config_{project_name}.json') as f:
            self.config = json.loads(f.read())