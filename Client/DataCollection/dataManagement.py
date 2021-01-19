"""
Different classes that are used to interface with different
database providers. 

Usable Clients: MongoDB.

"""
from pymongo import MongoClient
from typing import IO
from abc import ABC, abstractmethod
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
    @abstractmethod
    def getCIK(self, tickerSymbol: str) -> str:
        raise NotImplementedError("Implement method.")
    
    @abstractmethod
    def __writeStockQuote(self, tickerSymbol: str, separatedLines: list[str], separator: str):
        """ 
            
            To overide this function give the following function declaration:
            def _DatabaseClient__writeCIK(self, separatedLines: list[str], separator: str):
                # implementation
                .
                .
                .
            
            Prevents the issue of name mangling at the time of definition of the
            class.
        
            Helper function to write a stock quote to a DatabaseClient. """
        raise NotImplementedError("Implement method.")

    @abstractmethod
    def __writeCIK(self, separatedLines: list[str], separator: str):
        """ 
            Helper function to write the CIK numbers for a publicly traded
            company to find their SEC filings to a DatabaseClient. 
            
            To overide this function give the following function declaration:
            def _DatabaseClient__writeCIK(self, separatedLines: list[str], separator: str):
                # implementation
                .
                .
                .
            
            Prevents the issue of name mangling at the time of definition of the
            class.
            
        """
        raise NotImplementedError("Implement method.")

    def parseDate(self, date: str) -> datetime.date:
        return datetime.datetime.strptime(date, "%Y-%m-%d")

    def writeText(self, tickerSymbol: str, text: str, sep: str):
        """  
            Writes a stock quote to a database based on a separatorType.
            
            ----------------------------------------------------------------------
            params:
                tickerSymbol: Ticker symbol that represents the specified publicly
                              traded companies.
                
                text: The text that is being parsed.

                sep: Separator the text file is deliminated by. Same meaning 
                     and use as in the str.split() method.
        """
        separators = [",", None]

        if sep in separators:
            self.__writeDeliminatedEntry(tickerSymbol, text, sep)
        else:
            print("Error writing to database.")

    def __writeDeliminatedEntry(self, tickerSymbol: str, text: str, separator: str):
        """
            Writes an entry to the Stocks database. Format is specified
            by other helper functtion.

            ----------------------------------------------------------------------
            Params:
                tickerSymbol: Ticker symbol that represents the specified publicly
                              traded companies.
                text: The text that is being parsed.

        """
        # Separate the lines from the file.
        separatedLines = text.split(sep='\n')

        if separator == ",":
            self.__writeStockQuote(tickerSymbol, separatedLines, separator)
        elif separator == None:
            self.__writeCIK(separatedLines, separator)


class MongoDB(DatabaseClient):
    """ MongoDB database client implementation. """
    def __init__(self):
        #super(DatabaseClient, self).__init__()
        self.client = MongoClient()
        self.StocksDB = self.client["Stocks"]
        
    def _DatabaseClient__writeStockQuote(self, tickerSymbol: str, separatedLines: list[str], separator: str):
        """
            Sideaffect: Removes the first element from separatedLines.

            -----------------------------------------
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

        # Get the data titles and remove the first line from the list.
        headers = separatedLines[0].split(separator)
        separatedLines.pop(0)

        # Create and insert an entry for each individual stock quote.
        for line in separatedLines:
            values = line.split(separator)

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

    def _DatabaseClient__writeCIK(self, separatedLines: list[str], separator: str):
        """ Values are hard coded becasue format should never change. """
        # Create or get the current collection.
        self.StocksDB["CIK_ID"].drop()
        cik_collection = self.StocksDB["CIK_ID"]
        
        for line in separatedLines:
            values = line.split(separator)

            # Database entry
            entry = {
                "Symbol": str(values[0]).upper(),
                "CIK": int(values[1])
            }
            cik_collection.insert_one(entry)

    def getCIK(self, tickerSymbol: str) -> str:
        """ 
            Returns the string reperesentation of the CIK number
            for a companies ticker symbol.
        """
        cik_collection = self.StocksDB["CIK_ID"]
        document = cik_collection.find_one({"Symbol": tickerSymbol.upper()})

        if document is None:
            return None
        else:
            return str(document["CIK"])
        