"""
    Test file for testing the DataCollection modules.

"""
import unittest
import datetime

import context
from context import dataManagement



class Test_dataBaseManagement_write(unittest.TestCase):
    def test_1(self):
        dbClient = dataManagement.MonogDB()
        dbClient.writeStockQuotes()

    def test_2(self):
        pass


if __name__ == "__main__":
    unittest.main()