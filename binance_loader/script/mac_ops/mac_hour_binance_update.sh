cd vectorbt-research
python3 binance_loader/binance_updater.py --symbol_list select --timeframe 1h --product SPOT
python3 binance_loader/binance_updater.py --symbol_list select --timeframe 1h --product UPERP
cd ~