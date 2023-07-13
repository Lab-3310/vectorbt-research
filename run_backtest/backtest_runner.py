import os, sys
import platform
import argparse


sys.path.insert(1, os.path.dirname(__file__) + '/..')

# add new strategy 
from strategies.bband_example_mean_reversion import BbandCrossMeanReversionStrategy
from strategies.bband_example import BbandCrossExampleStrategy
from strategies.double_ema_plus_sma import DoubleEMAPlusSMA
from strategies.double_sma_example import DoubleSmaExampleStrategy
from strategies.example_strategy import ExampleStrategy
from strategies.stdma_strategy import STDMAStrategy
from strategies.dmi_strategy import DMIStrategy
from strategies.momentum_strategy import MomentumStrategy


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="backtest option")
    parser.add_argument('--strategy_class', '-class',required=True ,help='MM account') 
    parser.add_argument('--strategy_config', '-config',required=True, help='MM project name')

    args = parser.parse_args()
    strategy_class = args.strategy_class
    strategy_config = args.strategy_config

    strategy = DMIStrategy(strategy_class, strategy_config)
    # TODO
    # make this class uniform
    strategy.run_backtest()


    