import sys, os
# for linux
# sys.path.insert(1, '/home/chouwilliam/vectorbt-research')

# for macos
# sys.path.insert(1, '/Users/chouwilliam/vectorbt-research')

# for windows dog
sys.path.insert(1, r'C:\Users\William Harper\vectorbt-research')

from strategies.example_strategy import ExampleStrategy
from strategies.double_sma_example import DoubleSmaExampleStrategy
from strategies.bband_example import BbandCrossExampleStrategy