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
    
    def test_MongoDB(self):
        client = yf.DownloadHistoricalStock(DataBaseClientType.MONGODB)
        self.assertEqual(type(client.dBClient), type(dataManagement.MongoDB()))
    
    def test_download(self):
        pass
        """
        tickerSymbol = "MSFT"
        startDate = datetime.date(########)
        endDate = datetime.date(######)


        client.download()
        """



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