"""
Parses the SEC archives to find relevant forms on companies. 

"""
import requests
import bs4
from enum import Enum
import json
import datetime
from bs4 import BeautifulSoup
import time
import re
import logging

# Logging Settings
#logging.basicConfig(filename="ParseSEC.log", level=logging.DEBUG)


# Base archive url for the SEC EDGAR database.
SEC_BASE_ARCHIVE_URL = r"https://www.sec.gov/Archives/edgar/data/"

# Text file that contains the CIK number associated with diferent ticker symbols.
PATH_TO_SYMBOLS_TICKERS = r"C:\Users\rennt\Desktop\StockPrograms\Data\ticker.txt"

# Indexes for the ticker table object to parse a text file delimited by spaces.
TICKER_INDEX = 0
CIK_INDEX = 1
DELIMINATOR = None

class TickerTable(dict):
    """ Should only be used with the SEC website. """
    def __init__(self):
        self._tickerTable = self._getTickerTable()

    def __getitem__(self, item: str):
        return self._tickerTable[item]

    def _getTickerTable(self):

        table = {}
        with open(PATH_TO_SYMBOLS_TICKERS) as fp:
            for line in fp:
                symbol_CIK = line.split(DELIMINATOR)
                table.setdefault(symbol_CIK[TICKER_INDEX], symbol_CIK[CIK_INDEX])
                
        return table

    def __setitem__(self, item):
        raise NotImplementedError("Can't set item.")
    

class FormType(Enum):
    ten_K = 0
    ten_Q = 1
    eight_K = 2
    NoForm = 100


class Parser:
    """ Default parser only parses data past 2015. """
    def __init__(self, startDate = datetime.datetime(2020, 1, 1), endDate = datetime.datetime.now()):
        self.tickerTable = TickerTable()
        self.basePath = SEC_BASE_ARCHIVE_URL
        self.startDate = startDate
        self.endDate = endDate
    
    def getDocumentByCompany(self, form: FormType, tickerSymbol: str):
        """ Returns a parsed document of relevant information. """
        CIK = self.tickerTable[tickerSymbol]
        companyURL = self.basePath + CIK + '/'
        directoryURL = companyURL + "index.json"
        
        # Debugging 
        logging.debug(f"Company Directory URL: {directoryURL}")

        # Get the index file for the accession numbers directory
        response = requests.get(directoryURL)
        directoryIndex = response.json()['directory']['item']
        response.close()
        for item in directoryIndex:
            accessionNumber = item['name']
            submissionLastChange = datetime.datetime.strptime(item['last-modified'], "%Y-%m-%d %H:%M:%S")
            if  submissionLastChange >= self.startDate:
                accessionURL = companyURL + item["name"] + '/'
                submissionIndex = accessionURL + 'index.json'
                response = requests.get(submissionIndex)
                submissionFiles = response.json()["directory"]["item"]
                response.close()

                # Debugging 
                logging.debug(f"Accesion Index Directory URL: {submissionIndex}")

                for file in submissionFiles:
                    headerFileURL = None
                    if file["name"][-18:] == "index-headers.html":
                        headerFileURL = accessionURL + file["name"]
                        
                        # Debugging
                        logging.debug(f"Index Header URL: {headerFileURL}")

                    if headerFileURL != None:
                        response = requests.get(headerFileURL)
                        soup = BeautifulSoup(response.content, "html.parser")
                        text = soup.get_text()
                        typed = re.compile(r"<TYPE>.+")
                        formT = typed.findall(text)[0][6:]
                            
                        print(formT, headerFileURL)
                
            else:
                break

            time.sleep(0.5)