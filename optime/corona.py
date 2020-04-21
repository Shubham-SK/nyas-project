"""
Retrieves Case Data form NY Times.
"""
from places import Stores
#from uszipcode import SearchEngine
import csv
import urllib.request
import codecs
from datetime import datetime, timedelta
from pytz import timezone

class Cases:
    DATE = 0
    COUNTY = 1
    STATE = 2
    FIPS = 3
    CASES = 4
    DEATHS = 5

    def __init__(self):
        pass

    def get_cases(self, county, state):
        """
        county: (string) county name
        ---
        return: (arr<date, county, state, cases, deaths>)
        """
        # get retrieve CSV data
        url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
        ftpstream = urllib.request.urlopen(url)
        csvfile = csv.reader(codecs.iterdecode(ftpstream, 'utf-8'))

        now = datetime.now().replace(tzinfo=timezone('US/Eastern')) - timedelta(days=1)
        # yesterday = "%s-%s-%s" % (now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"))

        cases = []

        for line in csvfile:
            if (#line[self.DATE] == yesterday and
                line[self.COUNTY] == county and
                line[self.STATE] == state):
                cases.append(line)

        return cases

    def SEIR_analysis(self, case_data):
        """
        case_data: 
        ---
        return: r0
        """

# Testing
# case = Cases()
# print(case.get_cases("Contra Costa", "California"))
