"""
Uses ClimaCell API to schedule outting.
"""
from datetime import timedelta
from datetime import datetime as dt
import pytz
from climacell import Weather

weather = Weather() # pylint: disable=C0103

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
    total_time_delta = (end_time-start_time).total_seconds()

    # make sure paramters are valid
    try:
        assert now_time <= start_time < end_time # chronology
        assert end_time <= now_time+timedelta(days=15) # ensure 15 day scope
        assert duration <= (end_time-start_time).total_seconds()  # duration check
    except AssertionError:
        print(f'invalid parameters provided.')

    # get datetime objects for API time bounds
    nowcast_end = now_time+timedelta(seconds=weather.nowcast_end)
    hourly_end = now_time+timedelta(seconds=weather.hourly_end)
    daily_end = now_time+timedelta(seconds=weather.daily_end)

    # array to store raw data obtained the API
    weather_data = []
    fields = ['temp', 'humidity', 'humidity:%']

    print(f'total time delta: {total_time_delta} secs')

    # populate weather_data array with nowcast
    if total_time_delta > 0 and start_time < nowcast_end:
        # determine relative bounds
        relative_start_time = start_time
        relative_end_time = min(end_time, nowcast_end)
        # call API
        data = weather.get_nowcast(
            lat, lon, 5, 'us', fields,
            relative_start_time.isoformat(), relative_end_time.isoformat()
        )
        # append data
        weather_data.append(data)
        # update variables for next timestep
        total_time_delta -= round(
            (relative_end_time-start_time).total_seconds()
        )
        relative_start_time = relative_end_time

    print(f'after nowcast: {total_time_delta} secs')

    # populate weather_data array with hourly
    if total_time_delta > 0 and relative_start_time < hourly_end:
        # determine relative bounds
        relative_end_time = min(end_time, hourly_end)
        # call API
        data = weather.get_hourly(
            lat, lon, 'us', fields,
            relative_start_time.isoformat(), relative_end_time.isoformat()
        )
        # append data
        weather_data.append(data)
        # update variables for next timestep
        total_time_delta -= round(
            (relative_end_time-relative_start_time).total_seconds()
        )
        relative_start_time = relative_end_time

    print(f'after hourly: {total_time_delta} secs')

    # populate weather_data array with daily
    if total_time_delta > 0 and relative_start_time < daily_end:
        # determine relative bounds
        relative_end_time = min(end_time, daily_end)
        # call API
        data = weather.get_daily(
            lat, lon, 'us', fields,
            relative_start_time.isoformat(), relative_end_time.isoformat()
        )
        # append data
        weather_data.append(data)
        # update variables for next timestep
        total_time_delta -= round(
            (relative_end_time-relative_start_time).total_seconds()
        )

    print(f'after daily: {total_time_delta} secs')

    # make sure data has been logged for the entire time frame
    try:
        assert total_time_delta <= 0
    except AssertionError:
        print("error in time processing.")

    return weather_data

# Testing
# now_time = dt.utcnow().replace(tzinfo=pytz.utc)
# start_time = now_time + timedelta(hours=1)
# end_time = now_time + timedelta(days=10)
# print(f'start: {start_time}')
# print(f'end: {end_time}')
# print(schedule(10, 10, start_time, end_time, 10800))
