"""
Uses ClimaCell API to schedule outting.
"""
from climacell import Weather
from datetime import datetime as dt
from datetime import timedelta
import dateutil.parser
import pytz
import time

weather = Weather()

def schedule(lat, lon, start_time, end_time, duration):
    """
    Returns optimal time to go out.
    ---
    lat: (num) -59.9, 59.9
    lon: (num) -180, 180
    start_time: (datetime object)
    end_time: (datetime object)
    duration: (num) seconds
    """
    # calculate time difference to make correct API call
    now_time = dt.utcnow().replace(tzinfo=pytz.utc)
    start_time_delta = (start_time-now_time).seconds
    total_time_delta = (end_time-start_time).seconds

    # make sure paramters are valid
    try:
        assert(now_time <= start_time < end_time) # chronology
        assert(end_time <= now_time+timedelta(days=15)) # ensure 15 day scope
        assert(duration <= (start_time-end_time).seconds) # duration check
    except AssertionError:
        print(f'invalid parameters provided.')

    # get datetime objects for API time bounds
    nowcast_end = now_time+timedelta(seconds=weather.nowcast_end)
    hourly_end = now_time+timedelta(seconds=weather.hourly_end)
    daily_end = now_time+timedelta(seconds=weather.daily_end)

    # get ISO formatted timestamps
    iso_start_time = start_time.isoformat()
    iso_end_time = end_time.isoformat()
    iso_nowcast_end = nowcast_end.isoformat()
    iso_hourly_end = hourly_end.isoformat()
    iso_daily_end = daily_end.isoformat()

    # array to store raw data obtained the API
    weather_data = []
    fields = ['temp', 'humidity', 'humidity:%']

    # populate weather_data array
    if total_time_delta > 0:
        relative_end_time = min(end_time, nowcast_end)
        # ADD API CALL
        total_time_delta -= (relative_end_time-start_time).seconds
    if total_time_delta > 0:
        relative_start_time = nowcast_end
        relative_end_time = min(end_time, hourly_end)
        # ADD API CALL
        total_time_delta -= (relative_end_time-relative_start_time).seconds
    if total_time_delta > 0:
        relative_start_time = hourly_end
        relative_end_time = min(end_time, daily_end)
        # ADD API CALL
        total_time_delta -= (relative_end_time-relative_start_time).seconds

    try:
        assert(total_time_delta < 0)
    except AssertionError:
        print("error in time processing.")



# Testing
# start_time = dt.utcnow().replace(tzinfo=pytz.utc) + timedelta(hours=1)
# end_time = dt.utcnow().replace(tzinfo=pytz.utc) + timedelta(hours=4)
#
# print(start_time, end_time)

print(schedule(10, 10, start_time, end_time, 10800))
