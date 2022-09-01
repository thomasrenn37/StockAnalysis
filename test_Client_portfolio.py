"""
    Test file for testing the DataCollection modules.

"""
import unittest
from copy import deepcopy


from Client.portfolio import Stock, Portfolio, InvalidRemovalOfSharesException, InsufficientFundsException


class Test_ClientPortfolio(unittest.TestCase):
    def setUp(self):
        stocks = [Stock("MSFT", 200, 5), Stock("AAPL", 250, 7)]
        self.port = Portfolio(1000.0, 1000.0, stocks)

    def test_Init(self):
        stocks = [Stock("MSFT", 200, 5), Stock("AAPL", 250, 7)]
        self.port = Portfolio(1000.0, 1000.0, stocks)

        portStocks = self.port.Stocks

        st = portStocks["MSFT"]
        self.assertEqual(st.NumShares, 5)
        self.assertEqual(st.AvgCost, 200)

        st = portStocks["AAPL"]
        self.assertEqual(st.NumShares, 7)
        self.assertEqual(st.AvgCost, 250)

    def testOwnedValidBuyStock(self):
        self.port.buyStock("MSFT", 5, 200.0)
        self.assertEqual(self.port.CashForInvestment, 0)
        self.assertEqual(self.port.NetCash, 0)
        self.assertEqual(self.port.Stocks["MSFT"].NumShares, 10)

    def testNewValidBuyStock(self):
        self.port.buyStock("V", 5, 150.0)
        self.assertEqual(self.port.CashForInvestment, 250)
        self.assertEqual(self.port.NetCash, 250)
        self.assertEqual(self.port.Stocks["V"].NumShares, 5)

    def testInValidBuyStock(self):
        self.assertRaises(InsufficientFundsException, self.port.buyStock, "MSFT", 20, 200.0)
        portStocks = self.port.Stocks

        st = portStocks["MSFT"]
        self.assertEqual(st.NumShares, 5)
        self.assertEqual(st.AvgCost, 200)
        self.assertEqual(self.port.CashForInvestment, 1000)
        self.assertEqual(self.port.NetCash, 1000)

    def testInvalidSellStock(self):
        self.assertRaises(KeyError, self.port.sellStock, "V", 2, 100)
        self.assertEqual(self.port.CashForInvestment, 1000)
        self.assertEqual(self.port.NetCash, 1000)

    def testValidSellStock(self):
        self.port.sellStock("MSFT", 2, 100)
        self.assertEqual(self.port.CashForInvestment, 1000)
        self.assertEqual(self.port.NetCash, 1200)
        self.assertEqual(self.port.Stocks["MSFT"].NumShares, 3)


class Test_StockClass(unittest.TestCase):
    def setUp(self):
        self.stock = Stock("MSFT", 200.0, 8)

        assert (self.stock.NumShares == 8)
        assert (self.stock.AvgCost == 200.0)
        assert (self.stock.TickerSymbol == "MSFT")
        assert (self.stock.TotalCost == 1600.0) 

    def test_percentGain(self):
        assert (self.stock.percentGain(250.0) == 0.25)
        assert (self.stock.percentGain(150.0) == -0.25)
        assert (self.stock.percentGain(200.0) == 0.0)

    def test_addShares(self):
        self.stock.addShares(4, 200.0)
        self.assertEqual(self.stock.NumShares, 12)
        self.assertEqual(self.stock.AvgCost, 200.0)
        self.assertEqual(self.stock.TotalCost, 2400)

        self.stock.addShares(4, 250)
        self.assertEqual(self.stock.NumShares, 16)
        self.assertEqual(self.stock.AvgCost, 212.5)
        self.assertEqual(self.stock.TotalCost, 3400)

    def test_invalidRemoveShares(self):
        self.assertRaises(InvalidRemovalOfSharesException, self.stock.removeShares, 40)

    def test_validRemoveShares(self):
        self.stock.removeShares(4)
        self.assertEqual(self.stock.NumShares, 4)
        self.assertEqual(self.stock.TotalCost, 800)

        self.stock.removeShares(4)
        self.assertEqual(self.stock.NumShares, 0)
        self.assertEqual(self.stock.TotalCost, 0)
        
    def test_TickerSymbol(self):
        assert (self.stock.TickerSymbol == "MSFT")


if __name__ == "__main__":
    test_classes_to_run = [Test_ClientPortfolio, Test_StockClass]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)
        
    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)