"""
These container classes do not store any type of market value besides the cost
of the equities.
"""
from typing import List, Dict
from abc import ABC
from copy import deepcopy, copy

class Equity(ABC):
    """ Abstract base class that represents a equity """
    def __init__(self, name: str, value: float):
        self._name = name
        self._totalCost = value

class Stock(Equity):
    """
    This is just a container to store the total cost, the average cost per share, the number of shares
    and the ticker symbol of a specific stock.

    Private memebers:
        _numShares (int): The number of shares of the stock.
        _totalCost (float): The total cost (number of shares * average cost per share)
        _numShares (int): The total number of shares of the stock.
        _name (str): Inherited from Equity is the ticker symbol of the stock.
    """
    def __init__(self, ticker_symbol: str, purchase_cost_per_share: float, shares: int):
        total_cost = purchase_cost_per_share * shares
        self._avgCost = purchase_cost_per_share
        self._numShares = shares
        Equity.__init__(self, ticker_symbol.upper(), total_cost)

    def __str__(self):
        frmt = f"""{self._name}\t{self._totalCost}\t{self._numShares}\t\t{(self._avgCost):.2f}"""
        return frmt

    def percentGain(self, currentValuePerShare: float) -> float:
        """ Calculates the percentage gain of the stock and returns it as a float. """
        return (currentValuePerShare - self._avgCost) / self._avgCost

    def addShares(self, numShares: int, costPerShare: float):
        """ 
        Adds numShares to the number of shares for the Stock instance and updates the 
        _totalCost, _numShares and _avgCost private members to reflect the added shares implact.
        """
        temp = self._totalCost + (numShares * costPerShare)
        self._totalCost = temp
        self._numShares += numShares
        self._avgCost = temp / self._numShares

    def removeShares(self, numShares: int):
        """ 
        Remove numShares from the Stock instance and updates the total cost of shares. 
        Raises InvalidRemovalOfSharesException if numShares is greater than the number of shares
        stored in the Stock instance.
        """
        # Exception if there are more more shares removed than there currently are.
        if numShares > self._numShares:
            raise InvalidRemovalOfSharesException(f"There {self.NumShares} of {self.TickerSymbol}. Tried to remove {numShares}")

        self._numShares -= numShares
        self._totalCost = self._numShares * self._avgCost
        
    @property
    def AvgCost(self) -> float:
        """ Get the average cost per share of the stock. """
        return self._avgCost
    
    @property
    def TotalCost(self) -> float:
        """ Get the total cost of all the shares. """
        return self._totalCost

    @property
    def NumShares(self):
        """ Get the number of shares for the Stock instance. """
        return self._numShares

    @property
    def TickerSymbol(self):
        """ Get the ticker symbol for the stock instance. """
        return self._name

"""
class Option(Equity):
    class OptionType(Enum):
        call = 0
        put = 1

    def __init__(self, type: OptionType, purchase_cost: float, shares: int, underlying_tickerSymbol: str):
        super().__init__(purchase_cost, shares, underlying_tickerSymbol)
        self.type = type
"""

class InvalidRemovalOfSharesException(Exception):
    """ 
    Indicates that the user has created an invalid removal of shares, such as more
    shares than are currently available.
    """
    def __init__(self, message):
        super().__init__(message)

class InsufficientFundsException(Exception):
    def __init__(self, message):
        super().__init__(message)



class Portfolio:
    """ 
    Container for settled cash available for investment, net cash, and stocks.
    
    private members:
        _stocks: a dictionary that maps a ticker symbol to a Stock instance. Stocks should only be
                added through the addStock method, so the program can map the ticker symbols to the 
                correct stock.

        _cashForInvestment (float): the amount of cash that is settled and available to purchase investments.
                This does not always mean the total cash in the Portfolio.

        _netCash (float): all the cash that is in the portfolio including cash not available for investment.
    """
    def __init__(self, cashForInvestment: float, netCash: float, stocks: List[Stock] = []):
        self._stocks: Dict[str, Stock] = {}

        for st in stocks:
            self._stocks[st.TickerSymbol] = Stock(st.TickerSymbol, st.AvgCost, st.NumShares)

        self._cashForInvestment = cashForInvestment
        self._netCash = netCash
        
    def __str__(self):
        frmt = f"Type\tEquity\t# Shares\tCostPerShare\n"
        for key in self._stocks:
            frmt += str(self._stocks[key]) + '\n'
    
        return frmt
    
    @property
    def CashForInvestment(self):
        return self._cashForInvestment
    
    @property
    def NetCash(self):
        return self._netCash
    
    @property
    def Stocks(self) -> Dict[str, Stock]:
        return deepcopy(self._stocks)

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

    def buyStock(self, tickerSymbol: str, numShares: int, perShareCost: float):
        """ Add a stock to the Porfolio instance. """
        # Check to see if there are enough funds available to purchase the amount of shares requested.
        if self._cashForInvestment - (numShares * perShareCost) < 0:
            raise InsufficientFundsException("Not enough net cash to purchase the number of shares requested.")

        # Check if ticker Symbol is in the _stocks dictionary.  
        if tickerSymbol in self._stocks:
            # add shares to existing symbol
            stock = self._stocks[tickerSymbol]
            stock.addShares(numShares, perShareCost)
        else:
            # Otherwise, add a new stock symbol to the _stocks dictionrary
            self._stocks[tickerSymbol] = Stock(tickerSymbol, perShareCost, numShares)

        # Update net cash and the cash for investments.
        self._netCash -= numShares * perShareCost
        self._cashForInvestment -= numShares * perShareCost

    def sellStock(self, tickerSymbol: str, numShares: int, sellValue: float):
        """ 
        Raises a KeyError if the tickerSymbol is not a key in the stocks dictionary.
        Raises a InvalidRemovalOfSharesException if numShares is greater than the number of shares
        stored in the stock instance mapped from tickerSymbol.
        """
        stock = self._stocks[tickerSymbol]

        # Remove the stock if we no longer own any shares. Otherwise update number of shares.
        if numShares == stock.NumShares:
            self._stocks.pop(tickerSymbol)
        else:
            stock.removeShares(numShares)

        # Update net cash. 
        self._netCash += numShares * sellValue

    """
    TODO: Add options later.

    def appendOptions(self, item: Option):
        assert type(Option) == type(Option)
        self.__options.append(item)
    
    def removeOpetion(self, item: Option):
        assert type(item) == type(Stock)
        self.__stocks.remove(item)
    """

