# StockAnalysis (Need to Know)
This repository is a side project I have been working on when I have free time with a few different and separate functionalities that do not currently work with a trading client and are not fully functional. This project will contain a collection of stock analysis tools and interfacing with specific brokerages API's.
#

## Client
Currently the only available API is with Etrade and is not fully functional. In order to use the trading client a user must have a brokerage account with ETrade in order to use this aspect and aquire permission from ETrade to use their API. Otherwise the tradingClient cannot be used.
#

## DataBaseClient
There should be some way for a trading client to store and access data. This is handled through the Client/DataCollection folder. The implementation can use the following database providers to store data:
- MongoDB
#
## Data Aquisition
The current implementation allows historical daily stock prices
to be downloaded from YahooFinace through the DownloadHistoricalStock object in yahooFinance. In the future, the SEC edgar fillings will hopefully be available.


