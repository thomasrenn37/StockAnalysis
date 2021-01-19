"""
    Sets the context for the test cases. Allows for easier imports
    within the test files.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Client')))
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Client', 'DataCollection')))

# Client imports
# import analysis
import etradeClient

# Data Collection imports
import DataCollection
import dataManagement
import parseSEC
import yahooFinance

from dataManagement import DataBaseClientType