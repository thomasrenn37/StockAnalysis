import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Client')))
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Client', 'DataCollection')))



import analysis
import client
import DataCollection.dataManagement
import DataCollection.ParseSEC
import DataCollection.YahooFinance