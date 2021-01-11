"""
    Test file for testing the DataCollection modules.

"""
import unittest
import datetime

import context
from context import dataManagement
from context import yahooFinance as yf
from context import DataBaseClientType


class Test_YahooFinance_MonogoDB(unittest.TestCase):
    def setUp(self):
        self.client = yf.DownloadHistoricalStock(DataBaseClientType.MONGODB)

    def test_MongoDB(self):
        self.assertEqual(type(self.client.dBClient), type(dataManagement.MongoDB()))
    
    def test_download(self):
        print("\nTesting download")
        tickerSymbol = "TSLA"
        startDate = datetime.date(2020, 1, 10)
        endDate = datetime.date(2021, 1, 10)

        self.client.download(tickerSymbol, startDate, endDate)
        



"""
class Test_YahooFinance_AnotherDBProvider(unittest.TestCase):
    def test_1(self):
        pass
        
        dbClient = dataManagement.MonogDB()
        dbClient.writeStockQuotes()
        

    def test_2(self):
        pass
"""

if __name__ == "__main__":
    unittest.main()