'''
    Library used for working with the eTrade Api to place trades for the account.

    Author: Thomas Renn

'''
import logging
import logging.handlers as handlers
import configparser
import webbrowser
from rauth import OAuth1Service
from typing import List
import sys
import json
from enum import Enum
import random, string

# User defined libraries
import portfolio as p
import analysis
from client import Client


# Debugging Logging settings
logger = logging.getLogger("client")
logger.setLevel(logging.INFO)
hand = handlers.RotatingFileHandler(filename="eTradeClient.Debug", maxBytes=5 * 1024 * 1024, backupCount=3)
hand.setLevel(logging.INFO)
debugging_fmt = logging.Formatter("%(asctime)s: %(message)s")
hand.setFormatter(debugging_fmt)
logger.addHandler(hand)

# Parses the configuration file for etrade account info
config = configparser.ConfigParser()
config.read(r"C:\Users\rennt\Desktop\StockPrograms\Client\config.ini")


def printJson(text: str):
    """ Helper function for debugging."""
    jObj = json.loads(text)
    print(json.dumps(jObj, indent=4))


def __oAuth(dev: bool):
    """ Gets the authorization from the ETrade website to access the API endpoints. Based on the
    default script given on the eTrade documentation website. Returns a authenticated session and 
    base url to make requests to the API endpoints. 
    """

    # Used for testing or for production
    if dev:
        base_url = config["DEFAULT"]["SAND_BASE_URL"]
        consumer_key = config["DEFAULT"]["SAND_CONSUMER_KEY"]
        consumer_secret = config["DEFAULT"]["SAND_CONSUMER_SECRET"]
    else:
        base_url = config["DEFAULT"]["PROD_BASE_URL"]
        consumer_key = config["DEFAULT"]["PROD_CONSUMER_KEY"]
        consumer_secret = config["DEFAULT"]["PROD_CONSUMER_SECRET"]

    etrade = OAuth1Service(
        name="etrade",
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
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


    return session, base_url


# --------------------------------------------------
# Etrade Client to place trades and analyze position
# --------------------------------------------------
class EtradeClient(Client):
    """
    Represents a client to place trades for the etrade platform.
    """
    NUMBER_OF_SYMBOLS_PER_CALL = 25

    def __init__(self, dev = True):
        self.dev = dev
        self.accountIdKey = self._getAccountID()
        self.session, self.base_url = __oAuth(dev)
        self.porfolio = self.__getPortfolio()
        super().__init__()

    def __str__(self):
        """ Prints the portfolio """
        return str(self.portfolio)
    
    # -------------------------------------
    # Stock Quote Methods -----------------
    # -------------------------------------

    def _getStockQuote(self, tickerSymbols: List[str]):
        """
            Returns a json object object of quote values for the given
            ticker symbols.
        """
        url = self.base_url + "/v1/market/quote/"
        for i in range(len(tickerSymbols)):
            if i != 0:
                url += (',' + tickerSymbols[i].name)
            else:
                url += tickerSymbols[i].name
        url += ".json"
        
        response = self.session.get(url)
        json_object = json.loads(response.text)
        #logger.info(f"Stock Lookup: {tickerSymbols}")
        return json_object

    def __getOptionChain(self, tickerSymbol: str):
        """ TODO: IMplement """
        url = self.base_url + "/v1/market/optionschains?symbol={" + tickerSymbol + "}"
        response = self.session.get(url)

        json_object = json.loads(response.text)
        return json_object


    # ---------------------------------------
    # Portfolio/Account Methods -------------
    # ---------------------------------------
    
    def _getAccountID(self):
        """ Returns the account key of a specified account """
        if self.dev:
            return config["DEFAULT"]["SAND_ACCOUNT_NUMBER"]
        else:
            return config["DEFAULT"]["ACCOUNT_NUMBER"]

    def __getPortfolio(self):
        # Urls to make requests
        accountURL = self.base_url + f"/v1/accounts/{self.accountIdKey}"
        balanceURL = accountURL + f"/balance.json"
        portfolioURL = accountURL + f"/portfolio.json"
        
        # Initialize the Portfolio container
        port = p.Portfolio()

        # Get the cash balance for the Portfolio container
        params = {"instType": "BROKERAGE", "realTimeNAV": "true"}
        response = self.session.get(balanceURL, params=params)
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
        response = self.session.get(portfolioURL)
        if response.status_code == 200:
            data = response.json()
        elif response.status_code == 204: # No data in response
            self.porfolio = port
            return
        else:
            raise NotImplementedError("Error retreiving the portfolio values response")

        # TODO: Append portfolio value to portfolio container

    def UpdatePortfolioValue(self, tickerSymbols: List[str]) -> None:
        """ Returns a dictionary of the values of the given stock symbols """
        data = self._getStockQuote(tickerSymbols)
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
    def _ordersURL(self):
        return self.base_url + "/v1/accounts/" + self.accountIdKey + "/orders"

    def listOrders(self):
        """ Lists previous orders """
        try:
            data = self.session.get(self._ordersURL()).json()
        except json.JSONDecodeError:
            print("Error: Data is None")
            return
        return data
    
    def cancelExistingOrders(self, orderID: int):
        """ Cancels an existing order given the specified orderID """
        url = self._ordersURL() + "/cancel"
        response = self.session.put(url, data={"accountIdKey": orderID})
        if response.status_code != 200:
            raise StatusCodeError(f"Status code: <{response.status_code}>.")
        

    def changeOrder(self, orderNumber: str):
        pass

    def placeStockOrder(self, limitPrice: float, quantity: int, symbol: str):
        """ Places a preview and an order of a specified stock. """
        # Step 1: Preview the order
        url = self._ordersURL() + "/preview.json"
        order = EquityOrder(limitPrice, quantity, symbol)
        headers = {"Content-Type": "application/json", "consumerKey": config["DEFAULT"]["PROD_CONSUMER_KEY"]}
        response = self.session.post(url, headers=headers, header_auth=True, data=order.PreviewRequest)
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
        url = self._ordersURL() + "/place.json"
        response = self.session.post(url, headers=headers, header_auth=True, data=order.PostRequest(previewId))
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
        self.porfolio.Cash

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

    