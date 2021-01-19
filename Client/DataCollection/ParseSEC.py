import requests
import bs4
from enum import Enum
import json
import datetime
from bs4 import BeautifulSoup
import time
import re
from dataManagement import DatabaseClient


class FormType(Enum):
    TEN_K = 0
    TEN_Q = 1
    EIGHT_K = 2
    NO_FORM = 100


class SECParser:
    """ Default parser only parses data past 2015. """
    # Base archive url for the SEC EDGAR database.
    SEC_BASE_ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/"
    TICKER_PATH = "https://www.sec.gov/include/ticker.txt"
    def __init__(self, databaseClient: DatabaseClient, startDate = datetime.datetime(2020, 1, 1), endDate = datetime.datetime.now()):
        self.dBClient = databaseClient
        self.startDate = startDate
        self.endDate = endDate
    
    def updateCIKs(self):
        """ Writes the CIK numbers to a database client. """
        # Url for the CIK to ticker file.
        response = requests.get(self.TICKER_PATH)
        self.dBClient.writeText("", response.text, None)

    def getDocumentByCompany(self, tickerSymbol: str): # form: FormType,
        """ 
            Returns a parsed document of relevant information. 
            --------------------------------------------------
            Params: 
                form: The form type to be returned.
                tickerSymbol: The ticker symbol for a stock. 
        """
        # Get the URL for the request.
        CIK = self.dBClient.getCIK(tickerSymbol)
        directoryURL = self.SEC_BASE_ARCHIVE_URL + CIK + '/index.json'
        
        # Get the index file for the accession numbers directory
        response = requests.get(directoryURL)
        print(response.json()['directory']['item'][1])
        print(type(response.json()['directory']['item']))
        # dict_keys(['item', 'name', 'parent-dir'])
        response.close()

        """
        for item in directoryIndex:
            accessionNumber = item['name']
            submissionLastChange = datetime.datetime.strptime(item['last-modified'], "%Y-%m-%d %H:%M:%S")
            if  submissionLastChange >= self.startDate:
                accessionURL = companyURL + item["name"] + '/'
                submissionIndex = accessionURL + 'index.json'
                response = requests.get(submissionIndex)
                submissionFiles = response.json()["directory"]["item"]
                response.close()

                for file in submissionFiles:
                    headerFileURL = None
                    if file["name"][-18:] == "index-headers.html":
                        headerFileURL = accessionURL + file["name"]

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
        """
    