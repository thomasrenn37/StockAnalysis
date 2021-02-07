etradeClient docs:
    Etrade Client Object methods:

        - UpdatePortfolioValue()  - IMPLEMENT
        Updates the portolio values

        - listOrders()
        Returns a json object for the current orders.

        - cancelExistingOrders(orderID: int)
        Cancels the specified order by using the orderID for the order.

        - changeOrder(orderID: int) - IMPLEMENT

        - placeStockOrder(limitPrice: float, quantity: int, tickerSymbol: str)
        Places a preview and an order for that previewed order for the stock specified by ticker symbol.

        - placeOptionOrder(limitPrice: float, quantity: int, symbol: str) - IMPLEMENT

        - recordDailyPerformance() - IMPLEMENT

    Order Object methods:
        - _generateOrderRequest([previewId=0])
        Places a preview request order if the ID is 0. If the ID is specified then this is placing an order.
        Called by PostRequest.

        - PreviewRequest()
        Needs to be called first.


        - PostRequest()
        Places a post request to place order.

        - _generateOrderRequest()
        A reference number used to ensure no duplicate orders have
        been submitted. Returns a string of 20 or less alphanumeric characters. 


    Types of Orders:
        - EquityOrder
        - OptionOrder - IMPLEMENT


    Errors: 
        - StatusCodeError- Explains a status code error


    Enums:
        - OrderType - Specifies an order type

    Functions:
        - printJson - prints the json values given a string.
        - _oAuth(dev: bool) - Gets the authorization from the ETrade website to access the API endpoints. Based on the
                            default script given on the eTrade documentation website. Returns a authenticated session and 
                            base url to make requests to the API endpoints. 

    Constants:
        - NUMBER_OF_SYMBOLS_PER_CALL = 25


portfolio module:
    Equity object - Abstract base class that represents a equity 
        methods:
            - totalValue - returns the total value of a equity 
            - percentageGain() - returns the total percentage gain.

    Cash(Equity):
        methods:
            - updateAvailable - updates the value.

    Stock(Equity):
        methods:
            -  

    Option(Equity):
        methods:
            -  

    Portfolio(Equity):
        methods:
            -  
