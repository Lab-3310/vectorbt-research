from strategies.example_strategy import ExampleStrategy
from strategies.double_sma_example import DoubleSmaExampleStrategy

strategy_class = 'DoubleSmaExampleStrategy'
strategy_config = 'double_ma_example_config_01'

example_strategy = DoubleSmaExampleStrategy(strategy_class, strategy_config)
example_strategy.run_backtest()