from typing import List
import datetime
from abc import ABC, abstractmethod
from enum import Enum


class Equity(ABC):
    """ Abstract base class that represents a equity """
    def __init__(self, cost_per_share: float, shares: int, name: str):
        self.name = name
        self.costPerShare = cost_per_share
        self.shares = shares
        self.currentValue = (None, datetime.datetime.now())
        super(Equity, self).__init__()
    
    def totalValue(self):
        return cost_per_share * shares
    
    def percentageGain(self):
        return self.totalValue() / self.costPerShare

    @abstractmethod
    def __str__(self):
        pass


class Cash(Equity):
    def __init__(self, value: float, buyingPower: float, shares = 1, name = "CASH"):
        self.value = value
        self.buyingPower = buyingPower
        super().__init__(value, shares, name)

    def updateAvailable(self, amount: float):
        self.value = amount

    def __str__(self):
        frmt = f"""{str(self.__class__)[-7:-2] :<8}{self.name :>3} {str(self.shares):>6}\
        {str(self.currentValue[0]):<16}{self.currentValue[1]}"""

        return frmt


class Stock(Equity):
    def __init__(self, purchase_cost: float, shares: int, ticker_symbol: str):
        super().__init__(purchase_cost, shares, ticker_symbol.upper())

    def perShareCost(self):
        return self.purchaseCost / self.shares

    def percentageGain(self):
        if self.currentValue[0] is not None:
            return (self.currentValue - self.perShareCost())
        else:
            return None

    def __str__(self):
        frmt = f"""{str(self.__class__)[-7:-2] :<8}{self.name :>3} {str(self.shares):>6}\
        {str(self.currentValue[0]):<16}{self.currentValue[1]}"""

        return frmt


class Option(Equity):
    class OptionType(Enum):
        call = 0
        put = 1

    def __init__(self, type: OptionType, purchase_cost: float, shares: int, underlying_tickerSymbol: str):
        super().__init__(purchase_cost, shares, underlying_tickerSymbol)
        self.type = OptionType



class Portfolio:
    def __init__(self, cash: Cash):
        self.__stocks = []
        self.__options = []
        self.__cash = 0
        self.__totalValue = 0
        
    @property
    def Cash(self):
        return self.__cash

    def appendStocks(self, item: Stock):
        assert type(Stock) == type(Stock)
        self.__stocks.append(item)

    def removeStocks(self, item: Stock):
        assert type(item) == type(Stock)
        self.__stocks.remove(item)

    def appendOptions(self, item: Option):
        assert type(Option) == type(Option)
        self.__options.append(item)
    
    def removeOpetion(self, item: Option):
        assert type(item) == type(Stock)
        self.__stocks.remove(item)

    def __str__(self):
        frmt = f"Type    Equity  #_Shares   CurrentValue    LastQuery\n"
        for equity in self.equities:
            frmt += str(equity) + '\n'
    
        return frmt

    def currentValues(self, symbol_value: dict):
        for symbol in self.equities:
            try:
                symbol.currentValue[0] = symbol_value[symbol.name]
                symbol.currentValue[1] = datetime.datetime.now()
                
            except KeyError:
                print(f"Error updating {symbol.name}")
                pass
