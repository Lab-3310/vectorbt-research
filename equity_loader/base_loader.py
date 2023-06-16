import datetime
import logging
import time
from datetime import timedelta
from enum import Enum
import pandas as pd

class SinoBroker(Enum):
    SINO = 'sino'
    TWEQ = 'tweq'
    FUTURE = 'future'
    PERSON_ID = 'person_id'
    PASSWORD = 'pass_wd'


class BaseLoader:
    def __init__(self):
        self._get_broker_config = {}

    @property
    def get_broker_config(self):
        return self._get_broker_config