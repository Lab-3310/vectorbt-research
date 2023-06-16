import os, sys
sys.path.insert(1, os.path.dirname(__file__) + '/../..')

from equity_loader.sino_loader import SinoLoader

def main():
    sino_loader = SinoLoader()
    sino_loader.download_future_df()

if __name__ == '__main__':
    main()