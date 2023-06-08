cd vectorbt-research
python3 binance_loader/binance_updater.py --symbol_list select --timeframe 1m --product SPOT
python3 binance_loader/binance_updater.py --symbol_list select --timeframe 1m --product UPERP
cd ~