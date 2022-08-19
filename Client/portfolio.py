"""
Classes (see classess for more detail on specifics):
    Equity: The abtract base class used in all of the subclasses of an Equity.


Enums: 
    CurrencyType: Used along side with the Currency class for later implementation. TODO

"""
from typing import List, Dict
import datetime
from abc import ABC
from enum import Enum
from copy import deepcopy


class Equity(ABC):
    """ Abstract base class that represents a equity """
    def __init__(self, name: str, value: float, date_time: datetime.datetime = datetime.datetime.now()):
        self.name = name
        self._value_time = (value, date_time)
    
    def totalValueAndTime(self):
        return self._value_time


class CurrencyType(Enum):
    USD = 0
    EURO = 1


class Currency(Equity):
    def __init__(self, value: float, buyingPower: float = 0, type = CurrencyType.USD):
        if buyingPower == 0:
            self._buyingPower = value
        super().__init__(type.name, value)

    def updateBuyingPower(self, amount: float):
        self._buyingPower = self._buyingPower - amount

    def __str__(self):
        frmt = f"Buying Power: {self._buyingPower}\nTotal Cash: ${self.totalValue()}"

        return frmt

    def updateValue(self, amount: float):
        # Update the buying power if it was not already updated.
        if self._buyingPower == self._value_time[0]:
            self._buyingPower += amount
        
        self._value_time = (self._value_time[0] + amount, datetime.datetime.now())

    def totalValue(self) -> float:
        return self._value_time[0]

    @property
    def BuyingPower(self):
        return self._buyingPower

class Stock(Equity):
    """
    Field memembers:
        _num_shares (int): the number of shares of the stock.

    Inherits field values: 
        name (str): The ticker symbol for the stock.
        _value_time (Tuple (float, datetime)): the value of the stock at a datetime.
    """
    def __init__(self, purchase_cost_per_share: float, shares: int, ticker_symbol: str):
        value = purchase_cost_per_share * shares
        self._num_shares = shares
        Equity.__init__(self, ticker_symbol.upper(), value)

    def avgerageCost(self) -> float:
        """ Returns the cost per share for the stock. """
        return self.totalValue() / self._num_shares

    def percentGain(self) -> float:
        """ Calculates the percentage gain of the stock. """
        if self.currentValue[0] is not None:
            return (self.currentValue - self.averageCost()) / 100
        else:
            return None

    def totalValue(self) -> float:
        return self._value_time[0]

    def __str__(self):
        frmt = f"""{self.name}\t{self.totalValue()}\t{self._num_shares}\t\t{(self.perShareCost()):.2f}\t\t{self.totalValueAndTime()[1]}"""

        return frmt

    @property
    def NumShares(self):
        return self._num_shares

    @property
    def Ticker(self):
        return self.name

    def UpdateValueAndTime(self, value: float, time: datetime.datetime = datetime.datetime.now()) -> None:
        # value is number of shares * current price the stock is valued at.
        self._value_time = (value, time)

"""
class Option(Equity):
    class OptionType(Enum):
        call = 0
        put = 1

    def __init__(self, type: OptionType, purchase_cost: float, shares: int, underlying_tickerSymbol: str):
        super().__init__(purchase_cost, shares, underlying_tickerSymbol)
        self.type = type
"""

class OrderCode(Enum):
    CANT_AFFORD = -3
    INCORRECT_AMOUNT = -2
    STOCK_NOT_IN_PORTFOLIO = -1
    SUCCESS = 0

class Portfolio:
    def __init__(self, cash: Currency, stocks: Dict[str, Stock] = {}):
        self._stocks = deepcopy(stocks)
        self._cash = cash
        self._totalValue = cash.totalValueAndTime()[0]
        
        if len(stocks):
            for ticker in stocks.keys():
                self._totalValue += stocks[ticker].totalValue()

        #self._options = []
        
    @property
    def Cash(self):
        return deepcopy(self._cash)
    
    @property
    def Stocks(self):
        return deepcopy(self._stocks)

    def appendStocks(self, item: Stock):
        assert(type(Stock) == type(Stock))
        self._stocks.append(item)

    def removeStocks(self, item: Stock):
        assert(type(item) == type(Stock))
        self._stocks.remove(item)

    def SellStock(self, ticker_symbol: str, amount: int, sell_value: float) -> OrderCode:
        # Check if the portfolio contains the stock being sold 
        if ticker_symbol not in self._stocks:
            return OrderCode.STOCK_NOT_IN_PORTFOLIO

        stock = self._stocks[ticker_symbol]
        cash = self._cash
        if amount < stock.NumShares:
            stock._num_shares -= amount
            stock.UpdateValueAndTime(sell_value * stock.NumShares)
            cash._value_time = ((amount * sell_value) + cash._value_time[0], datetime.datetime.now())

        elif amount == stock.NumShares:
            stock._num_shares -= amount
            cash._value_time = ((amount * sell_value) + cash._value_time[0], datetime.datetime.now())
            self._stocks.pop(ticker_symbol)

        else:
            return OrderCode.INCORRECT_AMOUNT

        return OrderCode.SUCCESS        

    def BoughtStock(self, ticker_symbol: str, amount: int, buy_val: float) -> OrderCode.CANT_AFFORD:
        # Check if the amount of stock can be purchased with the amount of buying power
        if amount * buy_val > self.Cash.BuyingPower:
            return OrderCode.CANT_AFFORD
        
        # Check if the stock is already owned and update amount of shares owned
        if ticker_symbol in self._stocks:
            stock = self._stocks[ticker_symbol]
            stock._num_shares += amount

            # Update the stock value
            stock.UpdateValueAndTime(amount * buy_val, datetime.datetime.now()) 
        else:
            self._stocks[ticker_symbol] = Stock(buy_val, amount, ticker_symbol)

        # Update the cash amount
        self._cash.updateValue(-(amount * buy_val))

        return OrderCode.SUCCESS

    """
    TODO: Add options later.

    def appendOptions(self, item: Option):
        assert type(Option) == type(Option)
        self.__options.append(item)
    
    def removeOpetion(self, item: Option):
        assert type(item) == type(Stock)
        self.__stocks.remove(item)
    """


    def __str__(self):
        frmt = f"Type\tEquity\t# Shares\tCurrentValue\tLastQuery\n"
        for equity in self._stocks:
            frmt += str(equity) + '\n'
    
        return frmt

    def PrintPortfolio(self) -> None:
        # Print the cash amount
        divider = "----------------------------------------------"

        print('\n' + divider)
        print("Cash Details")
        print(self._cash)
        print("\n" + "Stock Details")
        
        print(f"Type\tEquity\t# Shares\tCurrentValue\tLastQuery")
        for stock in self._stocks:
            print(self._stocks[stock])

        print(divider)

    """
    def currentValues(self, symbol_value: dict):
        for symbol in self.equities:
            try:
                symbol.currentValue[0] = symbol_value[symbol.name]
                symbol.currentValue[1] = datetime.datetime.now()
                
            except KeyError:
                print(f"Error updating {symbol.name}")
                pass
    """