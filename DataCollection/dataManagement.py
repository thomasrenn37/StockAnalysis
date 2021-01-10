"""
Different classes that are used to interface with different
database providers. 

Usable Clients: MongoDB.

"""
from pymongo import MongoClient
from abc import ABC



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

    def writeStockQuotes(self, file_stream):
        if 
        
        