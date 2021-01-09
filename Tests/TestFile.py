import sys
sys.path.append(r"C:\Users\rennt\Desktop\StockPrograms\Client")
import unittest
import DataCollection.ParseSEC as ps
import Client.etradeClient as client
import Client.analysis as Analysis
import Client.portfolio as pf
import DataCollection.YahooFinance as yf
import datetime


class TestSECParcer(unittest.TestCase):
    """
    def testClient(self):
        stock = pf.Stock(66, 1, "MSFT")
        stock_2 = pf.Stock(88, 3, "AAPL") 
        stock_3 = pf.Stock(9999, 7, "AMZN") 
        
        stocks = []
        stocks.append(stock)
        stocks.append(stock_2)
        stocks.append(stock_3)
        port = pf.Portfolio(stocks)
        
        etrade = client.EtradeClient()
        print(etrade.listOrders())
    """
    
    def testOrder(self):
        etrade = client.EtradeClient(False)
        etrade.placeEquityOrder(190, 1, "MSFT")

        

if __name__ == "__main__":
    unittest.main(warnings='ignore')