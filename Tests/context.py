"""
    Sets the context for the test cases. Allows for easier imports
    within the test files.
"""
import os
import sys
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Client')))
#print(sys.path)
# Client imports

from ..Client import analysis as analysis
from ..Client.tradingClient import tradingClient as client
from ..Client.portfolio import portfolio as portfolio

# Data Collection imports
import Client.DataCollection.dataManagement as dataManagement 
import Client.DataCollection.parseSEC as parseSEC
import Client.DataCollection.yahooFinance as yahooFinance

#from Client.DataCollection.dataManagement import DataBaseClientType