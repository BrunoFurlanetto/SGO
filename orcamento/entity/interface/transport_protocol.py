from abc import ABC, abstractclassmethod
from ..basevalue import BaseValue

class TransportProtocol(ABC, BaseValue):
    def __init__(self, values, periods, days):
        super().__init__(values)
        self.periods=periods
        self.days=days
        self.min_payers = 30
    
    def set_min_payers(self, min_payers):
        self.min_payers = min_payers
        return self.min_payers        

    @abstractclassmethod
    def calc_value_transport(self, is_transport):
        pass