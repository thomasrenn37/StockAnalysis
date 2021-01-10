"""
orders module.

Describes an order type. 


"""
from enum import Enum

class OrderType(Enum):
    EQ = 1
    OPTN = 2
    SPREADS = 3


#TODO: Create way to overide default options

class Order:
    """
    An order class used to generate order requests via a client object.

    """
    def __init__(self, orderType: OrderType, limitPrice: float, 
    quantity: int, symbol: str, allOrNone = "false", priceType = "LIMIT", 
    orderTerm = "GOOD_FOR_DAY", marketSession = "REGULAR", stopPrice = ""):
        # Order values
        self._orderType = orderType.name
        self._allOrNone = allOrNone
        self._priceType = priceType
        self._orderTerm = orderTerm
        self._marketSession = marketSession
        self._stopPrice = stopPrice
        self._limitPrice = limitPrice
        self._symbol = symbol
        self._quantity = quantity
        self._clientOrderID = self._generateOrderId()

    def __generateOrderRequest(self, previewId=0) -> str:
        """ 
        Params: 
            previewId (int): Leave as 0 if an order is being previewed. Else use a previously
                            generated previewId to post an order.

        Returns a string representation in json syntax of the instance order request.

        Leave the default previewId if this is a preview order. To get dictionairy
        for posting order, give the previewId for the correct order.
        """
        # Determines if the request is a preview or order
        if previewId:
            title = "PlaceOrderRequest"
        else:
            title = "PreviewOrderRequest"

        order = {
            title: {
                "orderType":self._orderType,
                "clientOrderId":self._clientOrderID,
                "Order": [
                    {
                        "allOrNone":self._allOrNone,
                        "priceType":self._priceType,
                        "orderTerm":self._orderTerm,
                        "marketSession":self._marketSession,
                        "stopPrice":self._stopPrice,
                        "limitPrice":self._limitPrice,
                        "Instrument":[
                            {
                                "Product":{
                                    "securityType":self._orderType,
                                    "symbol":self._symbol
                                },
                                "orderAction":"BUY",
                                "quantityType":"QUANTITY",
                                "quantity":str(self._quantity)
                            }
                        ]
                    }
                ]
            } 
        }

        if previewId:
            order[title]["PreviewIds"] = [{"previewId":previewId}]
        return json.dumps(order)

    @property
    def PreviewRequest(self):
        return self.__generateOrderRequest()
        
    def PostRequest(self, previewId: int) -> str:
        return self.__generateOrderRequest(previewId)

    def _generateOrderId(self) -> str:
        """ A reference number used to ensure no duplicate orders have
        been submitted. Returns a string of 20 or less alphanumeric characters. 
        """
        orderId = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 20)))
        return orderId

    def __str__(self):
        return self.__previewOrderRequest


class EquityOrder(Order):
    """ Represents an equity order that inherits from the Equity base class """
    def __init__(self, limitPrice: float, quantity: int, symbol: str):
        super().__init__(OrderType.EQ, limitPrice, quantity, symbol)


# TODO: finish updating OptionOrder
class OptionOrder(Order):
    """ Represents an option order that inherits from the Equity base class """
    def __init__(self, limitPrice: float, quantity: int, symbol: str):
        super().__init__(OrderType.OPTN, limitPrice, quantity, symbol)