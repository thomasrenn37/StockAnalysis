"""
Abstract class used to define a client object that can access a  single
brokerage account and perform operations for that specific account.
"""

from abc import ABC, abstractmethod
import analysis


class Client(ABC):
    """ Abstract base class for the implementation of the trading client. """
    def __init__(self):
        self.porfolio = self._getPortfolio()
        self.indicators = []
        super(Client, self).__init__()

    @abstractmethod
    def _getPortfolio(self):
        pass

    def addIndicator(self, indicator: analysis.Indicators):
        self.indicators.append(indicator)

    def listIndicators(self) -> list:
        indicators = []
        for ind in self.indicators:
            indicators.append(ind)
        return indicators



