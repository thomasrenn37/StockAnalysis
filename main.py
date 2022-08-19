from Client.tradingClient import EtradeClient
import time

def main():
    client = EtradeClient(False)
    tickers = ['TGT', 'VYM', 'INTC', 'BROS', 'NFLX']
    quotes = client.getMultipleStockQuotes(tickers)
    
    for q in quotes:
        print(f"SYM: {q.symbol} Last: ${q.lastTrade} {time.gmtime(q.dateTimeUTC)}")
        print(f"volume: {q.averageVolume}")
        print(f"day low:${q.low} day high:${q.high}")
        print()

if __name__ == "__main__":
    main()