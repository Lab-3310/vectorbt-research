
from datetime import datetime

FUTURE_SINCE = datetime(2020, 3, 23).strftime('%Y-%m-%d')
EQUITY_SINCE = datetime(2018, 12, 7).strftime('%Y-%m-%d')
NOW = datetime.now().strftime('%Y-%m-%d') 

FUTURE_TICKER = [
    "MXFR1",
    "ZFFR1",
    "ZEFR1",
    # "UNFR1",
    # "UDFR1",
] # TODO -> Find more ticker support by SINO API

MIN = '1m'
FUTURE = 'future'
EQUITY = 'equity'

