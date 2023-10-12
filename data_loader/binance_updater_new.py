import os
import sys

sys.path.insert(1, os.path.expanduser('~/Systematic-Sherpa/'))

from data_handler.binance_handler import BinanceHandler


if __name__ == '__main__':

    handler = BinanceHandler()
    handler.handler_download()