"""
Uses ClimaCell API to schedule outting.
"""
from climacell import Weather
from datetime import datetime as dt
import dateutil.parser

weather = Weather()

def schedule(start_time, end_time, duration):
    """
    Returns optimal time to go out.
    ---
    start_time: (ISO 8601 time stamp) ex: 2019-03-20T14:09:50Z
    end_time: (ISO 8601 time stamp) ex: 2019-03-20T14:09:50Z
    duration: (num) minutes
    """
    start_time = dateutil.parser.parse(start_time)
    end_time = dateutil.parser.parse(end_time)

    time_difference = end_time - start_time

    return time_difference
