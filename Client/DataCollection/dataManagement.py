"""
Different classes that are used to interface with different
database providers. 

Usable Clients: MongoDB.

"""
from pymongo import MongoClient
from typing import IO
from abc import ABC
from enum import Enum

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


class MonogDB(DatabaseClient):
    def __init__(self):
        super.__init__()

    def writeStockQuotes(self, file_stream: IO):
        """ Writes a stock quote to a database. """
        print(file_stream.name)
        
        