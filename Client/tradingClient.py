import configparser
import webbrowser
from rauth import OAuth1Service
from typing import List
import json
from enum import Enum
import random, string
from abc import ABC, abstractmethod
import os.path

# User defined libraries
import Client.portfolio as porfolio
import Client.analysis as analysis



def printJson(jsonObj):
    """ Helper function for debugging."""
    print(json.dumps(jsonObj, indent=4))



class TradingClient(ABC):
    """
        Abstract class used to define a client object that can access a  single
        brokerage account and perform operations for that specific account.
    """
    def __init__(self):
        super().__init__()

    def placeOptionOrder(self, limitPrice: float, quantity: int, symbol: str):
        raise NotImplementedError("Implement method.")

    def UpdatePortfolioValue(self, tickerSymbols: List[str]) -> None:
        raise NotImplementedError("Implement method.")

    def cancelExistingOrders(self, orderID: int):
        raise NotImplementedError("Implement method.")

    def changeOrder(self, orderNumber: str):
        raise NotImplementedError("Implement method.")

    def placeStockOrder(self, limitPrice: float, quantity: int, symbol: str):
        raise NotImplementedError("Implement method.")

    def placeOptionOrder(self, limitPrice: float, quantity: int, symbol: str):
        raise NotImplementedError("Implement method.")

    def recordDailyPerformance(self):
        """ Returns a dictionairy, where keys desd"""
        pass

    def addIndicator(self, indicator: analysis.Indicators):
        self.indicators.append(indicator)

    """
    def listIndicators(self) -> list:
        indicators = []
        for ind in self.indicators:
            indicators.append(ind)
        return indicators
    """


# --------------------------------------------------
# Etrade Client to place trades and analyze position
# --------------------------------------------------
class EtradeClient(TradingClient):
    """
    Represents a client to place trades for the etrade platform.
    """
    __Max_NUMBER_OF_SYMBOLS_PER_CALL = 25

    def __init__(self, dev = True):
        self.__dev = dev
        
        # Parses the configuration file for etrade account configurations.
        if os.path.exists("Client/config.ini"):
            self.__config = configparser.ConfigParser()
            self.__config.read("Client/config.ini")
        else:
            exit(0)

        # Setting configurations for instance category.
        if dev:
            self.__base_url = self.__config["DEFAULT"]["SAND_BASE_URL"]
            self.__consumer_key = self.__config["DEFAULT"]["SAND_CONSUMER_KEY"]
            self.__consumer_secret = self.__config["DEFAULT"]["SAND_CONSUMER_SECRET"]
            self.__accountIdKey = self.__config["DEFAULT"]["SAND_ACCOUNT_NUMBER"]
        else:
            self.__base_url = self.__config["DEFAULT"]["PROD_BASE_URL"]
            self.__consumer_key = self.__config["DEFAULT"]["PROD_CONSUMER_KEY"]
            self.__consumer_secret = self.__config["DEFAULT"]["PROD_CONSUMER_SECRET"]
            self.__accountIdKey = self.__config["DEFAULT"]["ACCOUNT_NUMBER"]

        # Create and verify an oath session.
        self.__session = self.__oAuth()

        # Populate the portfolio container with current values.
        #self.__porfolio = self.__getPortfolio()
        self.indicators = []

    def __str__(self):
        """ Prints the portfolio """
        return str(self.portfolio)

    def __oAuth(self):
        """ 
        Gets the authorization from the ETrade website to access the API endpoints. 
        Returns a authenticated session and base url to make requests to the API endpoints
        as a tuple.

        Based on the source code given on the eTrade documentation website that can be found at:
        https://developer.etrade.com/home 
        """
        etrade = OAuth1Service(
            name="etrade",
            consumer_key=self.__consumer_key,
            consumer_secret=self.__consumer_secret,
            request_token_url="https://api.etrade.com/oauth/request_token",
            access_token_url="https://api.etrade.com/oauth/access_token",
            authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
            base_url="https://api.etrade.com")

        # Step 1: Get OAuth 1 request token and secret
        request_token, request_token_secret = etrade.get_request_token(
            params={"oauth_callback": "oob", "format": "json"})

        # Step 2: Go through the authentication flow. Login to E*TRADE.
        # After you login, the page will provide a text code to enter.
        authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
        webbrowser.open(authorize_url)
        text_code = input("Please accept agreement and enter text code from browser: ")

        # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
        session = etrade.get_auth_session(request_token,
                                        request_token_secret,
                                        params={"oauth_verifier": text_code})

        return session
    
    # -------------------------------------
    # Stock Quote Methods -----------------
    # -------------------------------------

    def __getStockQuote(self, tickerSymbols: List[str]):
        """
            Returns a json object of quote values for the given
            ticker symbols.
        """
        url = self.__base_url + "/v1/market/quote/" + tickerSymbols[0]

        for i in range(1, len(tickerSymbols)):
            url += (',' + tickerSymbols[i])

        url += ".json"
        
        response = self.__session.get(url)
        json_object = json.loads(response.text)
        return json_object

    def StockQuote(self, ticker: str):
        printJson(self.__getStockQuote([ticker]))

    def __getOptionChain(self, tickerSymbol: str):
        """ TODO: IMplement """
        url = self.__base_url + "/v1/market/optionschains?symbol={" + tickerSymbol + "}"
        response = self.__session.get(url)

        json_object = json.loads(response.text)
        return json_object

    # ---------------------------------------
    # Portfolio/Account Methods -------------
    # ---------------------------------------
    


    def __getPortfolio(self) -> p.Portfolio:
        """ 
            Returns a Portfolio object of the current account specified in the
            instance of the EtradeClient class.
                
        """
        # Urls to make requests
        accountURL = self.__base_url + f"/v1/accounts/{self.__accountIdKey}"
        balanceURL = accountURL + f"/balance.json"
        portfolioURL = accountURL + f"/portfolio.json"
        
        # Initialize the Portfolio container
        port = p.Portfolio()

        # Get the cash balance for the Portfolio container
        params = {"instType": "BROKERAGE", "realTimeNAV": "true"}
        response = self.__session.get(balanceURL, params=params)
        data = response.json()

        if data is not None and "BalanceResponse" in data:
            computed = data["BalanceResponse"]["Computed"]
            investableCash = computed["cashAvailableForInvestment"]
            netCash = computed["netCash"]
            c = p.Cash(netCash)
            port.append(c)
        else:
            raise NotImplementedError("Error retreiving the balance response")

        # Get portfolio items
        response = self.__session.get(portfolioURL)
        if response.status_code == 200:
            data = response.json()
        elif response.status_code == 204: # No data in response
            self.__porfolio = port
            return
        else:
            raise Exception("Error retreiving the portfolio values response")

        # TODO: Append portfolio value to portfolio container

    def UpdatePortfolioValue(self, tickerSymbols: List[str]) -> None:
        """ Returns a dictionary of the values of the given stock symbols """
        data = self.__getStockQuote(tickerSymbols)
        #print(data)
        
        # TODO: Fix for all ticker symbols once real data available

        allItems = data['QuoteResponse']['QuoteData'][0]["All"]
        productName = data['QuoteResponse']['QuoteData'][0]["Product"]['symbol']
        value = allItems["ask"]
        
        symbol_value = {productName: value}
        # Parse the json object for the current value and datetime

        self.portfolio.currentValues(symbol_value) 

    # -------------------------------------
    # Order Methods -----------------------
    # -------------------------------------
    
    def __ordersURL(self) -> str:
        return self.__base_url + "/v1/accounts/" + self.__accountIdKey + "/orders"

    def listOrders(self) :
        """ Lists previous orders """
        try:
            data = self.__session.get(self.__ordersURL()).json()
        except json.JSONDecodeError:
            data = None
        return data
    
    def cancelExistingOrders(self, orderID: int):
        """ Cancels an existing order given the specified orderID """
        url = self.__ordersURL() + "/cancel"
        response = self.__session.put(url, data={"accountIdKey": orderID})
        if response.status_code != 200:
            raise StatusCodeError(f"Status code: <{response.status_code}>.")

        return

    def changeOrder(self, orderNumber: str):
        pass

    def placeStockOrder(self, limitPrice: float, quantity: int, symbol: str):
        """ Places a preview and an order of a specified stock. """
        # Step 1: Preview the order
        url = self.__ordersURL() + "/preview.json"
        order = EquityOrder(limitPrice, quantity, symbol)
        headers = {"Content-Type": "application/json", "consumerKey": config["DEFAULT"]["PROD_CONSUMER_KEY"]}
        response = self.__session.post(url, headers=headers, header_auth=True, data=order.PreviewRequest)
        if response.status_code == 200:
            # Get the order Id
            data = response.json()
            print(json.dumps(data, indent=4))
            previewId = data["PreviewOrderResponse"]["PreviewIds"][0]["previewId"]
        elif response.status_code == 204:
            print("Request successful: No response data available.")
            return
        else:
            StatusCodeError(response.status_code)
            return
        
        # Step 2: Place the order
        url = self.__ordersURL() + "/place.json"
        response = self.__session.post(url, headers=headers, header_auth=True, data=order.PostRequest(previewId))
        if response.status_code == 200:
            data = response.text
            printJson(data)
        elif response.status_code == 204:
            print("Request successful: No response data available.")
            return
        else:
            raise StatusCodeError(response.status_code)
            return
    
        # Update buying power
        self.__porfolio.Cash

        # If successful, update portfolio

        pass



    def placeOptionOrder(self, limitPrice: float, quantity: int, symbol: str):
        pass


    # --------------------------------------
    # Recording data  ----------------------
    # --------------------------------------

    # The client should record its performance in order to track progress
    # TODO: Create database to record performance possibly in different file
    def recordDailyPerformance(self):
        """ Returns a dictionairy, where keys desd"""
        pass




class StatusCodeError(Exception):
    def __init__(self, status_code):
        self.message = f"Request Status Code Error Number: {status_code}"
        super().__init__(self.message)
