"""
Different classes that are used to interface with different
database providers. 

Usable Clients: MongoDB.

"""
from pymongo import MongoClient
from typing import IO
from abc import ABC
from enum import Enum
import datetime


class DataBaseClientType(Enum):
    """ Different database providers that are availalbe. """
    MONGODB = 0


class DatabaseClient(ABC):
    """ 
    An abstract base class that defines the methods all database clients should provide for
    data access and writing.
    """
    def __init__(self):
        raise NotImplementedError("DatabaseClient is an abstract base class and therefore should not be instansiated.")

    def writeStockQuotes(self):
        raise NotImplementedError("Implement method.")

    def __writeCSV(self, text: str):
        raise NotImplementedError("Implement method.")


class MongoDB(DatabaseClient):
    def __init__(self):
        self.client = MongoClient()
        self.StocksDB = self.client["Stocks"]

    def writeStockQuotes(self, tickerSymbol: str, text: str, separatorType: str):
        """  
            Writes a stock quote to a database based on a separatorType.
            
            ----------------------------------------------------------------------
            params:
                tickerSymbol: Ticker symbol that represents the specified publicly
                              traded companies.
                
                text: The text that is being parsed.

                separatorType: (.csv)
        """
        if separatorType == ".csv":
            self.__writeCSV(tickerSymbol,text)
        else:
            print("Error writing to database.")
        
    def __writeCSV(self, tickerSymbol: str, text: str):
        """
            Writes an entry to the Stocks database in the following format.

            ----------------------------------------------------------------------
            Params:
                tickerSymbol: Ticker symbol that represents the specified publicly
                              traded companies.
                text: The text that is being parsed.
            -----------------------------------------------------------------------

            Entry format example:
            {
                Date: 2020-02-10T00:00:00.000+00:00
                Open: 1905.369995
                High: 1906.939941
                Low: 1880
                Close: 1883.160034
                Adj Close: 1883.160034
                Volume: 2853700
            }
        """
        # Create or get the current collection.
        stockCollection = self.StocksDB[tickerSymbol]
        
        # Separate the lines from the file.
        separatedLines = text.split(sep='\n')

        # Get the data titles and remove the first line from the list.
        headers = separatedLines[0].split(',')
        separatedLines.pop(0)

        # Create and insert an entry for each individual stock quote.
        for line in separatedLines:
            values = line.split(',')

            # Database entry
            entry = {
                headers[0]: self.parseDate(values[0]),
                headers[1]: float(values[1]),
                headers[2]: float(values[2]),
                headers[3]: float(values[3]),
                headers[4]: float(values[4]),
                headers[5]: float(values[5]),
                headers[6]: int(values[6])
            }
            stockCollection.insert_one(entry)

    def parseDate(self, date: str) -> datetime.date:
        return datetime.datetime.strptime(date, "%Y-%m-%d")
        