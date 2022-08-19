"""
Different indicators that could be add


"""
from typing import List
from abc import ABC, abstractmethod
from Client.DataCollection import dataManagement


class Indicators(ABC):
    def __init__(self, data: List[float], period: int):
        if len(data) < period:
            raise ValueError("The list of data items must be greater than the stated time period used for calculations.")
        self._name = "NO_NAME_GIVEN"
        self.period = period
        self.data = data
        self._currentValue = None
        super(Indicators, self).__init__()
        
    @abstractmethod
    def _calculate(self):
        """ Method to calculate the indicator """
        pass
    
    @abstractmethod
    def graph(self):
        pass

    @property
    def Name(self):
        return self._name

    @property
    def currentValue(self):
        return self._currentValue


    
# ---------------------------------------
# Movement average indicators
# ----------------------------------------
class SimpleMovingAverage(Indicators):
    """ Assumes the period of the SMA is equal to the number of data points provided """
    def __init__(self, historicalPrices: List[float], period: int):
        super().__init__(historicalPrices, period)
        self._currentValue = self._calculate()
        self._name = "Simple Moving Average (SMA)"

    def calculatePastIndicator(self) -> List[float]:
        """ Returns a list of simple moving averages. """
        i = 0
        values = []
        while i < len(self.data) - self.period + 1:
            sma = 0
            for item in range(i, self.period + i):
                sma += self.data[item]

            values.append(sma / self.period)
            i += 1

        return values
 
    def _calculate(self):
        """ Returns the newest value available """
        return self.calculatePastIndicator()[-1]

    def graph(self):
        pass


class ExponentialMovingAverage(Indicators):
    def __init__(self, historicalPrices: List[float], period: int):
        super().__init__(historicalPrices, period)
        self._currentValue = self._calculate(period)
        self._name = "Exponential Moving Average (EMA)"

    def calculatePastIndicator(self) -> List[float]:
        """ Returns a list of ema values """
        values = [self.data[0]]
        ema = self.data[0]
        K = 2 / (self.period + 1)
        for i in range(1, len(self.data)):
            ema = (self.data[i] * K) + (ema * (1 - K))
            values.append(ema)

        return values
    
    def _calculate(self, period: int):
        return self.calculatePastIndicator()[-1]

    def graph(self):
        pass


# ---------------------------------------
# Momemntum Indicators
# ----------------------------------------
_RSI_OVER_BOUGHT = 70
_RSI_OVER_SOLD = 30

class RSI(Indicators):
    """ Indicates whether a security is possibly overbought or oversold. """
    def __init__(self, data: List[float], period: int = 14):
        super().__init__(data, period)

        if period > len(data):
            raise ValueError("Number of data items must be greater than period")

        self._currentValue = self._calculate()
        self._overSoldValue = _RSI_OVER_SOLD
        self._overBoughtValue = _RSI_OVER_BOUGHT 
        self._name = "Relative Strength Index (RSI)"

    def _calculate(self):
        # Find up days and downdays
        upDays = 0
        downDays = 0

        for i in range(1, len(self.data)):
            move = self.data[i] - self.data[i - 1]
            if move >= 0:
                upDays += move
            else:
                downDays += abs(move)

        RS = (upDays / 14) / (downDays / 14)
        RSI = (100 - (100 / (1 + RS)))

        return RSI

    @property
    def overBought(self):
        return self._currentValue > self._overBoughtValue

    @property
    def overSold(self):
        return self._currentValue < self._overSoldValue

    def graph(self):
        pass


class MACD(Indicators):
    def __init__(self, data: List[float], period: int):
        super().__init__(data, period)
        
        self._name = "Moving Average Convergence Divergence"
        self._currentValue = self._calculate()

    def _calculate(self):
        pass

    def graph(self):
        pass



def compoundCalculator(base_amount: float, rate: float, num_years: int, num_freq: int):
    assert period > 0

    return base_amount * ((1 + (rate / num_freq)) ** (num_years * num_freq)) 



"""
# Abstact Model class
class Model(ABC):
    def __init__(self):

        super(ABC, self).__init__()


# Black Scholes Model



class BlackScholes(Model):



def calculateBlackScholes(stockPrice: float, )


"""



