

from strategies.double_ema_plus_sma import DoubleEMAPlusSMA

strategy_class = 'DoubleEMAPlusSMA'
strategy_config = 'double_ema_plus_sma_config_01'
strategy = DoubleEMAPlusSMA(strategy_class, strategy_config)
strategy.run_backtest()
