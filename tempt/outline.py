



class BaseStrategy:
    def __init__(self) -> None:
        pass
    # -> get information json

    def symbol(self):
        return 'BTCUSDT'

    def exchange(self):
        return 'BYBIT'


class VBTStats:
    def __init__(self) -> None:
        pass
    # vbt feature

    def get_metric(self):
        #....
        return 
    
    def get_heatmap(self):
        return


class Optimizer:
    def __init__(self) -> None:
        pass
    #vbt feature

    def get_walkforwar_result(self):
        #code
        return 




class CustomizedStrategy(BaseStrategy, VBTStats, Optimizer):
    def __init__(self) -> None:
        super().__init__()

        self.exchange()
        self.get_metric()
        self.get_walkforwar_result()

    
    