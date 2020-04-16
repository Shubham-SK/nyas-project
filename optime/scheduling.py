"""
Uses ClimaCell API to schedule outting.
"""
from datetime import timedelta
from datetime import datetime as dt
import pytz
from climacell import Weather
import dateutil.parser as parser
import math

weather = Weather() # pylint: disable=C0103
weatherVals = {}

def clean_data(dictionary):
    """
    """
    for item in dictionary:
        items = []
        temp = float(item['temp']['value'])
        humid = float(item['humidity']['value'])
        items.append(temp)
        items.append(humid)
        observation_time = parser.parse(item['observation_time']['value'])
        observation_time = observation_time.replace(tzinfo=pytz.utc)
        weatherVals[observation_time] = items

def clean_daily(diccionario):
    """
    """
    for item in diccionario:
        items = []
        temp = float(item['temp'][1]['max']['value'])
        humid = float(item['humidity'][0]['min']['value'])
        items.append(temp)
        items.append(humid)
        observation_time = dt.strptime(item['observation_time']['value'], "%Y-%m-%d")
        observation_time = observation_time.replace(tzinfo=pytz.utc)
        weatherVals[observation_time] = items

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
    daily_end = now_time+timedelta(seconds=weather.daily_end-86400)

    # array for fields
    fields = ['temp', 'humidity', 'humidity:%']

    print(f'total time delta: {total_time_delta} secs')
    relative_start_time = start_time

    # populate weather_data array with nowcast
    if total_time_delta > 0 and start_time < nowcast_end:
        # determine relative bounds
        relative_end_time = min(end_time, nowcast_end)
        # call API
        data = weather.get_nowcast(
            lat, lon, 1, 'us', fields,
            relative_start_time.isoformat(), relative_end_time.isoformat()
        )
        for i in data:
            print(i)
            print
        # append data
        clean_data(data)
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
        clean_data(data)
        # update variables for next timestep
        total_time_delta -= round(
            (relative_end_time-relative_start_time).total_seconds()
        )
        relative_start_time = relative_end_time

    print(f'after hourly: {total_time_delta} secs')

    # populate weather_data array with daily
    if total_time_delta > 0 and relative_start_time < daily_end:
        # determine relative bounds
        relative_end_time = daily_end
        # call API
        data = weather.get_daily(
            lat, lon, 'us', fields,
            relative_start_time.isoformat(), relative_end_time.isoformat()
        )
        # append data
        clean_daily(data)
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

def window_slider(duration, alpha=1, beta=1, jjeku=1.01):
    """
    """
    bestStartTime = dt.utcnow().replace(tzinfo=pytz.utc)
    bestEndTime = dt.utcnow().replace(tzinfo=pytz.utc)
    # avgTemp = 0
    # avgHumid = 101
    avgIndex = 10**1000
    ctr = 0
    for start_time in weatherVals:
        for end_time in weatherVals:
            # compute average
            ctr += 1
            tempAvgIndex = (weatherVals[end_time][1]-weatherVals[end_time][0]) / ctr
            if (duration*jjeku >= (end_time-start_time).total_seconds() >= duration):
                ctr = 0
                if tempAvgIndex < avgIndex:
                    avgIndex = tempAvgIndex
                    bestStartTime = start_time
                    bestEndTime = end_time
    return (bestStartTime, bestEndTime)

# http://localhost:8000/schedule?duration=2&count=Hours&start=2020-04-16&end=2020-04-18&lat=37.7192448&long=-121.92645119999997
# Testing
# start_time = dt.strptime("2020-04-16", '%Y-%m-%d').replace(tzinfo=pytz.utc) + timedelta(seconds=10)
# now = dt.utcnow().replace(tzinfo=pytz.utc) + timedelta(seconds=10)
#
# # If the user specified today as the starting date
# if (start_time.strftime('%x') == now.strftime('%x')):
#     start_time = now
# end_time = dt.strptime("2020-04-18", '%Y-%m-%d').replace(tzinfo=pytz.utc)

# end_time = datetime.strptime("2020-04-18", '%Y-%m-%d').replace(tzinfo=pytz.utc)
# now_time = dt.utcnow().replace(tzinfo=pytz.utc)
# # start_time = now_time + timedelta(hours=1)
# # end_time = now_time + timedelta(days=2)
# print(f'start: {start_time}')
# print(f'end: {end_time}')
# schedule(10, 10, start_time, end_time, 7200)
# # print(weatherVals)
# print(f'ya so like: {window_slider(86400)}')
