import os
import sys

# sys.path.insert(1, os.path.expanduser('~/vectorbt-research/'))

sys.path.insert(1, os.path.dirname(__file__) + '/..')

# /Users/chouwilliam/Lab3310Projects/Systematic-Sherpa/binance_loader/download_binance.py

from data_handler.binance_handler import BinanceHandler


if __name__ == '__main__':

    handler = BinanceHandler()
    handler.handler_download()