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
    SEC_EDGAR_DATA_URL = "https://www.sec.gov/Archives/edgar/data/"
    SEC_EDGAR_DAILY_INDEX_URL = "https://www.sec.gov/Archives/edgar/daily-index/"
    SEC_EDGAR_FULL_INDEX_URL = "https://www.sec.gov/Archives/edgar/full-index/"
    TICKER_URL = "https://www.sec.gov/include/ticker.txt"
    
    def __init__(self, databaseClient: DatabaseClient, startDate = datetime.datetime(2020, 1, 1), endDate = datetime.datetime.now()):
        self.dBClient = databaseClient
        self.startDate = startDate
        self.endDate = endDate
    
    def updateCIKs(self):
        """ Writes the CIK numbers to a database client. """
        # Url for the CIK to ticker file.
        response = requests.get(self.TICKER_URL)
        self.dBClient.writeText("", response.text, "\t")

    def yearQuarter(self, date: datetime.date) -> str:
        """ 
            Returns the string representation of quarter used in 
            requests given a date.

            Example return values:  "2020/QTR1/", "2020/QTR2/", 
                                    "2020/QTR3/", "2020/QTR4/"

            QTR1 end date: March 31
            QTR2 end date: June 30
            QTR3 end date: September 30
            QTR4 end date: December 31
        """
        year_quarter = date.year

        # Find the current quarter.
        if date <= datetime.date(year_quarter, 3, 31):
            year_quarter = str(year_quarter) + "/QTR1/"
        elif date <= datetime.date(year_quarter, 6, 30):
            year_quarter = str(year_quarter) + "/QTR2/"
        elif date <= datetime.date(year_quarter, 9, 30):
            year_quarter = str(year_quarter) + "/QTR3/"
        else:
            year_quarter = str(year_quarter) + "/QTR4/"

        return year_quarter

    def parseLine(self, line: str) -> list:
        # TODO: Get 4th element for list. edgar/data/894871/0001493152-21-000653.txt
        values = []
        i = 0
        while i < len(line) - 2:
            if line[i] == " " and (line[i + 1].isalpha() or line[i + 1].isdigit()):
                item = ""
                i += 1
                while i < len(line) - 3:
                    item += line[i]
                    if line[i] == " " and line[i + 1]  == " ":
                        i += 1
                        break
                    
                    i += 1

                values.append(item)
            i += 1

        return values

    def getDocumentByCompany(self, tickerSymbol: str): # form: FormType,
        """ 
            Returns a parsed document of relevant information by accessing
            from.idx sorted documents via a GET request. 
            --------------------------------------------------
            Params: 
                form: The form type to be returned.
                tickerSymbol: The ticker symbol for a stock. 
        """
        # Get the URL for the request.
        # CIK = self.dBClient.getCIK(tickerSymbol)
        #directoryURL = self.SEC_EDGAR_DATA_URL + CIK + 'index.json'

        # Create the URL for the current fiscal quarter.
        today = datetime.date.today()
        curr_year_quarter = self.yearQuarter(today)        
        directoryURL = self.SEC_EDGAR_FULL_INDEX_URL + curr_year_quarter + "form.idx"

        # Separate response by line.
        response = requests.get(directoryURL)
        text = response.text
        separated_lines = text.split("\n")

        for line in separated_lines:
            if line[0:5] == "10-K ":
                print(line)
                print(self.parseLine(line))
                """
                n = line.split("  ")
                for space in n:
                    if 
                """
        response.close()

        # Get the index file for the accession numbers directory
        # CIK specified format (Accession items) dict_keys(['item', 'name', 'parent-dir'])


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
    