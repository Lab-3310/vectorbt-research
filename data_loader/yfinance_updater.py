import os
import sys

sys.path.insert(1, os.path.expanduser('~/vectorbt-research/'))

from data_handler.yfinance_handler import YFinanceHandler


if __name__ == '__main__':

    handler = YFinanceHandler()
    handler.handler_download()