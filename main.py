import argparse
import importlib
import os, sys

#TODO fix the Unable to import strategy class on the path issue in importing the strategy_class 

sys.path.insert(1, os.path.dirname(__file__) + '/..')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="backtest option")
    parser.add_argument('--strategy_class', '-class', required=True, help='strategy class')
    parser.add_argument('--strategy_config', '-config', required=True, help='strategy config')

    args = parser.parse_args()
    strategy_class_name = args.strategy_class
    strategy_config = args.strategy_config

    # Determine the full path to the 'strategies' directory
    strategies_dir = os.path.join(os.path.dirname(__file__), 'strategies')

    # Dynamically import the strategy class based on the provided class name
    try:
        strategy_module = importlib.import_module(f'strategies.{strategy_class_name}')
        strategy_class = getattr(strategy_module, strategy_class_name)
    except (ImportError, AttributeError):
        print(f"Error: Unable to import strategy class '{strategy_class_name}'")
        exit(1)

    strategy = strategy_class(strategy_config)
    strategy.run_backtest()
