"""
    Test file for testing the DataCollection modules.

"""
import unittest
import datetime
from copy import deepcopy


from Client.portfolio import Currency, Stock, Portfolio, CurrencyType, OrderCode

test_stocks = {
    "MSFT": Stock(221, 7, "MSFT"), 
    "AMZN": Stock(2200, 9, "AMZN"), 
    "V": Stock(88, 11, "V")
}

class Test_ClientPortfolio(unittest.TestCase):
    def test_setup_portfolio(self):
        port = Portfolio(
            cash=Currency(1200),
            stocks=deepcopy(test_stocks)
        )

        port_stocks = port.Stocks
        for st in test_stocks:
            assert port_stocks[st].perShareCost() == test_stocks[st].perShareCost()
            assert port_stocks[st].NumShares == test_stocks[st].NumShares
            assert port_stocks[st].Ticker == test_stocks[st].Ticker
        
        assert port.Cash.totalValue() == 1200
        assert port.Cash.BuyingPower == 1200

    def test_sell_all_of_MSFT(self):
        cash_amount = 1100
        port = Portfolio(
            cash=Currency(cash_amount),
            stocks=deepcopy(test_stocks)
        )
        num_shares = test_stocks["MSFT"].NumShares
        port.SellStock("MSFT", num_shares, 225)

        port_stocks = port.Stocks
        assert "MSFT" not in port_stocks 
            
        assert(port.Cash.totalValue() == (cash_amount + (225 * num_shares)))
        assert port.Cash.BuyingPower == cash_amount

        port.PrintPortfolio()

    def test_sell_partial_V(self):
        cash_amount = 100
        current_stock_price = 200
        ticker = "V"
        port = Portfolio(
            cash=Currency(cash_amount),
            stocks=deepcopy(test_stocks)
        )

        port_stocks = port.Stocks
        assert ticker in port_stocks 
        
        num_shares = test_stocks[ticker].NumShares - 2
        assert port.SellStock(ticker, num_shares, current_stock_price) == OrderCode.SUCCESS


        assert(port.Cash.totalValue() == (cash_amount + (current_stock_price * num_shares)))
        assert port.Cash.BuyingPower == cash_amount
        port.PrintPortfolio()

    def test_buy_more_of_V(self):
        cash_amount = 999
        current_stock_price = 111
        ticker = "V"
        port = Portfolio(
            cash=Currency(cash_amount),
            stocks=deepcopy(test_stocks)
        )

        port_stocks = port.Stocks
        assert ticker in port_stocks 
        
        num_shares = 7
        assert port.BoughtStock(ticker, num_shares, current_stock_price) == OrderCode.SUCCESS

        assert(port.Cash.totalValue() == (cash_amount - (current_stock_price * num_shares)))
        assert port.Cash.BuyingPower == (cash_amount - (current_stock_price * num_shares))
        port.PrintPortfolio()


    def test_buy_new_stock(self):
        pass


class Test_ClientYahoo(unittest.TestCase):
    def test_normal(self):
        pass


if __name__ == "__main__":
    unittest.main()