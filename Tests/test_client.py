#import context
#from context import client
#from context import dataManagement
import unittest
import datetime


from .context import analysis, portfolio, client
from .context import yahooFinance, parseSEC



class TestSECParcer(unittest.TestCase):
    def testClient(self):
        stock = portfolio.Stock(66, 1, "MSFT")
        stock_2 = portfolio.Stock(88, 3, "AAPL") 
        stock_3 = portfolio.Stock(9999, 7, "AMZN") 
        
        stocks = []
        stocks.append(stock)
        stocks.append(stock_2)
        stocks.append(stock_3)
        port = portfolio.Portfolio(stocks)
        
    
    def testOrder(self):
        """
        etrade = client.EtradeClient(False)
        etrade.placeEquityOrder(190, 1, "MSFT")
        """
        pass
        

if __name__ == "__main__":
    unittest.main()