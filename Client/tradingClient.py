import configparser
from email.quoprimime import quote
from rauth import OAuth1Service
from typing import List
import json
from abc import ABC, abstractmethod
import os.path
import webbrowser
import datetime

# User defined libraries
from Client.portfolio import Portfolio


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

    def cancelExistingOrders(self, orderID: int):
        raise NotImplementedError("Implement method.")

    def changeOrder(self, orderNumber: str):
        raise NotImplementedError("Implement method.")

    def placeStockOrder(self, limitPrice: float, quantity: int, symbol: str):
        raise NotImplementedError("Implement method.")

    def getStockQuote(self, ticker: str):
        raise NotImplementedError("Implement method.")

    """
    def recordDailyPerformance(self):
        # Returns a dictionairy, where keys desd
        raise NotImplementedError("Implement method.")

    def placeOptionOrder(self, limitPrice: float, quantity: int, symbol: str):
        raise NotImplementedError("Implement method.")
    """



class EtradeStockQuoteAll:
    """ All dates are encoded using epoch time using UTC. """
    def __init__(self, values: dict):
        self.symbol = values["Product"]["symbol"]
        self.dateTimeUTC: float = float(values["dateTimeUTC"])
        self.securityType = values["Product"]["securityType"]
        self.quoteStatus = values["quoteStatus"]
        self.afterHours: bool = values["ahFlag"]

        # 	Indicates whether an option has been adjusted due to a corporate action (for example, a dividend or stock split)
        self.adjustedFlag: bool = values["All"]["adjustedFlag"]

        # The current ask price, size and time of the ask for a security
        self.ask: float = values["All"]["ask"]
        self.askSize: int = values["All"]["askSize"]
        self.askTime = self._timestampToEpochUTC(values["All"]["askTime"])   # Convert to epcoch time

        # Code for the exchange reporting the bid price
        self.bidExchange: str = values["All"]["bidExchange"]
        
        # The current bid price, size and time of the bid for a security
        self.bid: float = values["All"]["bid"]
        self.bidSize: int = values["All"]["bidSize"]
        self.bidTime = self._timestampToEpochUTC(values["All"]["bidTime"])    # Convert to epcoch time

        # Dollar change of the last price from the previous close
        self.changeClose: float = values["All"]["changeClose"]
        
        # Percentage change of the last price from the previous close
        self.changeClosePercentage: float = values["All"]["changeClosePercentage"]

        # Company/symbolDescription
        self.companyName = values["All"]["companyName"]

        # Direction of movement; that is, whether the current price is higher or lower than the price of the most recent trade
        self.dirLast: str = values["All"]["dirLast"]
        
        # Cash amount per share of the latest dividend
        self.dividend: float = values["All"]["dividend"]

        # Earnings per share on rolling basis
        self.eps: float = values["All"]["eps"]

        # Projected Earnings per share for the next fiscal year 
        self.estEarnings: float = values["All"]["estEarnings"]

        # Date (in Epoch time) on which shareholders were entitled to receive the latest dividend
        self.exDividendDate = values["All"]["exDividendDate"]
        
        # Highest/low price at which a security has traded during the current day
        self.high = values["All"]["high"]
        self.low = values["All"]["low"]

        # 	Highest/lowest price at which a security has traded during the past year (52 weeks)
        self.high52 = values["All"]["high52"]
        self.low52 = values["All"]["low52"]

        # Price of the most recent trade of a security
        self.lastTrade = values["All"]["lastTrade"]

        # Price of a security at the current day's market open
        self.open = values["All"]["open"]

        # Official price at the close of the previous trading day
        self.previousClose: float = values["All"]["previousClose"]

        # Final volume from the previous market session
        self.previousDayVolume: int = values["All"]["previousDayVolume"]

        # Exchange code of the primary listing exchange for this instrument
        self.primaryExchange: str = values["All"]["primaryExchange"]

        # Total number of shares or contracts exchanging hands
        self.totalVolume: int = values["All"]["totalVolume"]

        # Uniform Practice Code identifies specific FINRA advisories detailing unusual circumstances; for example, extremely large dividends, when-issued settlement dates, and worthless securities
        # self.upc:int  # ignore for now

        self.marketCap: float = values["All"]["marketCap"]

        self.sharesOutstanding = values["All"]["sharesOutstanding"]

        # Will only have a value if the request specified to include the next earnings date.
        self.nextEarningDate = values["All"]["nextEarningDate"]

        # A measure of a stock's volatility relative to the primary market index
        self.beta = values["All"]["beta"]

        self.dividendYield = values["All"]["yield"]
        self.declaredDividend = values["All"]["declaredDividend"]
        self.dividendPayableDate: int = values["All"]["dividendPayableDate"]

        # The price to earnings ratio
        self.pe = values["All"]["pe"]

        # The date at which the price was the lowest/highest in the last 52 weeks;
        self.week52LowDate: int = values["All"]["week52LowDate"]
        self.week52HighDate: int = values["All"]["week52HiDate"]

        # 	The intrinsic value of the share
        self.intrinsicValue = values["All"]["intrinsicValue"]

        # 	The time when the last trade was placed
        self.timeOfLastTrade = values["All"]["timeOfLastTrade"]

        # Average volume value corresponding to the symbol
        self.averageVolume = values["All"]["averageVolume"]

    def _timestampToEpochUTC(self, timestamp: str) -> float:
        """ Etrade gives dates in the following format: 19:59:59 EDT 08-17-2022"""
        HOUR_OFFSET_FROM_EDT = -3 # Simple offset from EDT, which should not matter for analyzing stocks during the day.
                                    # Might be  some edge cases where this cause problems.
        
        # First split the time, timezone and date.
        dateTimeValues = timestamp.split(" ")
        if dateTimeValues[1] != "EDT":
            raise NotImplementedError(f"Does not know the offset to implement the {dateTimeValues[1]} timezone.")

        # Split into [hours, minutes, seconds]
        timeValues = dateTimeValues[0].split(":")

        # Split into [month, day, century year]
        dateValues = dateTimeValues[2].split("-")

        year = int(dateValues[2])
        month = int(dateValues[0])
        day = int(dateValues[1])
        hour = int(timeValues[0])
        minute = int(timeValues[1])
        second = int(timeValues[2])
        dt = datetime.datetime(year, month, day, hour + HOUR_OFFSET_FROM_EDT, minute, second)

        return dt.timestamp()

# --------------------------------------------------
# Etrade Client to place trades and analyze position
# --------------------------------------------------
class EtradeClient(TradingClient):
    """
    Represents a client to place trades for the etrade platform.
    """
    __Max_NUMBER_OF_SYMBOLS_PER_CALL = 25

    def __init__(self, dev = True):
        self._dev = dev
        
        # Parses the configuration file for etrade account configurations.
        if os.path.exists("Client/config.ini"):
            self._config = configparser.ConfigParser()
            self._config.read("Client/config.ini")
        else:
            raise ClientAuthorizationError("Client/config.ini does not exist.")

        # Setting configurations for instance category.
        if dev:
            self._base_url = self._config["DEFAULT"]["SAND_BASE_URL"]
            self._consumer_key = self._config["DEFAULT"]["SAND_CONSUMER_KEY"]
            self._consumer_secret = self._config["DEFAULT"]["SAND_CONSUMER_SECRET"]
            self._accountIdKey = self._config["DEFAULT"]["SAND_ACCOUNT_NUMBER"]
        else:
            self._base_url = self._config["DEFAULT"]["PROD_BASE_URL"]
            self._consumer_key = self._config["DEFAULT"]["PROD_CONSUMER_KEY"]
            self._consumer_secret = self._config["DEFAULT"]["PROD_CONSUMER_SECRET"]
            self._accountIdKey = self._config["DEFAULT"]["ACCOUNT_NUMBER"]

        # Create and verify an oath session.
        self._session = self.__Authorize()

        # Populate the portfolio container with current values.
        #self._porfolio = self.__getPortfolio()

    def __str__(self):
        message = f"""Etrade Client\n{self._porfolio}"""
        return message

    def __Authorize(self):
        """ 
        Gets the authorization from the ETrade website to access the API endpoints. 
        Returns a authenticated session. 

        Based on the source code given on the eTrade documentation website that can be found at:
        https://developer.etrade.com/home 
        """
        etrade = OAuth1Service(
            name="etrade",
            consumer_key=self._consumer_key,
            consumer_secret=self._consumer_secret,
            request_token_url="https://api.etrade.com/oauth/request_token",
            access_token_url="https://api.etrade.com/oauth/access_token",
            authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
            base_url=self._base_url)

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
    def _getStockResponse(self, tickerSymbols: List[str]):
        """
            Returns a json object of quote values for the given
            ticker symbols.
        """
        url = self._base_url + "/v1/market/quote/" + tickerSymbols[0]

        for i in range(1, len(tickerSymbols)):
            url += (',' + tickerSymbols[i])

        url += ".json"
    
        response = self._session.get(url)
        json_object = json.loads(response.text)

        return json_object

    def getStockQuote(self, ticker: str) -> EtradeStockQuoteAll:
        quote_data = self._getStockQuote([ticker])["QuoteResponse"]["QuoteData"]
        return EtradeStockQuoteAll(quote_data)

    def getMultipleStockQuotes(self, tickers: List[str]) -> List[EtradeStockQuoteAll]:
        quotes = []
        for q in self._getStockResponse(tickers)["QuoteResponse"]["QuoteData"]:
            quotes.append(EtradeStockQuoteAll(q))

        return quotes
        
    """
    def _getOptionChain(self, tickerSymbol: str):
        url = self._base_url + "/v1/market/optionschains?symbol={" + tickerSymbol + "}"
        response = self._session.get(url)

        json_object = json.loads(response.text)
        return json_object
    """

    # ---------------------------------------
    # Portfolio/Account Methods -------------
    # ---------------------------------------

    def __getPortfolio(self) -> Portfolio:
        """ 
        Returns a Portfolio object of the current account specified in the
        instance of the EtradeClient class.   
        """
        # Urls to make requests
        accountURL = self._base_url + f"/v1/accounts/{self._accountIdKey}"
        balanceURL = accountURL + f"/balance.json"
        portfolioURL = accountURL + f"/portfolio.json"
        
        # Initialize the Portfolio container
        port = p.Portfolio()

        # Get the cash balance for the Portfolio container
        params = {"instType": "BROKERAGE", "realTimeNAV": "true"}
        response = self._session.get(balanceURL, params=params)
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
        response = self._session.get(portfolioURL)
        if response.status_code == 200:
            data = response.json()
        elif response.status_code == 204: # No data in response
            self._porfolio = port
            return
        else:
            raise Exception("Error retreiving the portfolio values response")

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
    
    def _ordersURL(self) -> str:
        return self._base_url + "/v1/accounts/" + self._accountIdKey + "/orders"

    def listOrders(self) :
        """ Lists previous orders """
        try:
            data = self._session.get(self._ordersURL()).json()
        except json.JSONDecodeError:
            data = None
        return data
    
    def cancelExistingOrders(self, orderID: int):
        """ Cancels an existing order given the specified orderID """
        url = self._ordersURL() + "/cancel"
        response = self._session.put(url, data={"accountIdKey": orderID})
        if response.status_code != 200:
            raise StatusCodeError(f"Status code: <{response.status_code}>.")

        return

    def changeOrder(self, orderNumber: str):
        pass

    def placeStockOrder(self, limitPrice: float, quantity: int, symbol: str):
        """ Places a preview and an order of a specified stock. """
        # Step 1: Preview the order
        url = self._ordersURL() + "/preview.json"
        order = EquityOrder(limitPrice, quantity, symbol)
        headers = {"Content-Type": "application/json", "consumerKey": self._consumer_key}
        response = self._session.post(url, headers=headers, header_auth=True, data=order.PreviewRequest)
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
        response = self._session.post(url, headers=headers, header_auth=True, data=order.PostRequest(previewId))
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
        self._porfolio.Cash

        # If successful, update portfolio

        pass
    
    """
    def placeOptionOrder(self, limitPrice: float, quantity: int, symbol: str):
        pass
    """

    # --------------------------------------
    # Recording data  ----------------------
    # --------------------------------------

    # The client should record its performance in order to track progress
    # TODO: Create database to record performance possibly in different file
    def recordDailyPerformance(self):
        """ Returns a dictionairy, where keys desd"""
        pass



class ClientAuthorizationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class StatusCodeError(Exception):
    def __init__(self, status_code):
        self.message = f"Request Status Code Error Number: {status_code}"
        super().__init__(self.message)
