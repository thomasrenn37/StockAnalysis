"""
Class that downloads historical data from
Yahoo and stores the requested values using
MongoDB.
"""
import requests
from enum import Enum
import datetime
import dataManagement
from dataManagement import DatabaseClient


class Frequency(Enum):
    """ The frequency type for historical stock data. """
    DAY = 0
    WEEK = 1
    MONTH = 2


class DownloadHistoricalStock:
    """ Only works as back as far January 2nd, 2015. """
    DAY_FACTOR = 86400.0
    START_DATE_INT = 1420156800 # Jan 2, 2015
    START_DATE_OBJECT = datetime.date(2015, 1, 2) 

    def __init__(self, databaseClient: DatabaseClient):
        self.url = "https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={p1}&period2={p2}&interval=1d&events=history"
        self.dBClient = databaseClient

    def __dayToInt(self, date: datetime.date) -> int:
        """ Converts the date to the integer representation for url parameter. """
        difference = date - self.START_DATE_OBJECT
        dayInt = self.START_DATE_INT + (difference.days * self.DAY_FACTOR)
        return int(dayInt)

    def download(self, tickerSymbol: str, startDate: datetime.date, endDate: datetime.date):
        """
        Description: Writes the values found on the Yahoo finance website for the historical stock prices for a 
                     stock specified by tickerSymbol.

        Params:
            tickerSymbol:  The ticker symbol of a publicly traded company. (ex: "MSFT", "GOOG", "AMZN", etc.) 
            startDate:  The starting date for the requested data time frame. 
            endDate:  The end date for the requested data time frame.

        Errors:
            ValueError: Raises a ValueError if endDate occurs before startDate.
            HTTPError: raises exception if there is an error retrieving the response.
        """
        # Error handling if invalid dates are given.
        if startDate > endDate:
            raise ValueError("Variable startDate must be before endDate.")
        elif startDate < self.START_DATE_OBJECT:
            raise ValueError(f"Variable startDate must be after endDate.")
        
        # Calculate the parameters for web request.
        period1 = self.__dayToInt(startDate)
        period2 = self.__dayToInt(endDate)
        url = self.url.format(symbol = tickerSymbol, p1 = period1, p2=period2)
        
        # Writes an entry to a database given a stock quote.
        with requests.get(url) as response:
            response.raise_for_status()
            self.dBClient.writeText(tickerSymbol, response.text, ",")
