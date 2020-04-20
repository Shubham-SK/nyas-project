from places import Stores
#from uszipcode import SearchEngine
import csv
import urllib.request
import codecs
from datetime import datetime, timedelta
from pytz import timezone

DATE = 0
COUNTY = 1
STATE = 2
FIPS = 3
CASES = 4
DEATHS = 5

url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
ftpstream = urllib.request.urlopen(url)
csvfile = csv.reader(codecs.iterdecode(ftpstream, 'utf-8'))

now = datetime.now().replace(tzinfo=timezone('US/Eastern')) - timedelta(days=1)
yesterday = "%s-%s-%s" % (now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"))

cases = []
for line in csvfile:
    if (line[DATE] == yesterday):
        cases.append(line)
