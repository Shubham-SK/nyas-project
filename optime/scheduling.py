"""
Uses ClimaCell API to schedule outting.
For use in app.py, call schedule, then capture output from window_slider.
"""
from datetime import timedelta
from datetime import datetime as dt
import pytz
import dateutil.parser as parser
from climacell import Weather

WEATHER = Weather()
WEATHER_VALS = {}

def clean_data(dictionary):
    """
    Creates a dictionary - for get_nowcast and get_hourly API response
    ---
    dictionary: WEATHER_VALS
    key: (datetime object)
    value: (arr<float>) [temperature (deg F), humidity (%)]
    """
    print(dictionary)
    for item in dictionary:
        items = []
        temp = float(item['temp']['value'])
        humid = float(item['humidity']['value'])
        items.append(temp)
        items.append(humid)
        observation_time = parser.parse(item['observation_time']['value'])
        observation_time = observation_time.replace(tzinfo=pytz.utc)
        WEATHER_VALS[observation_time] = items


def clean_daily(dictionary):
    """
    Creates a dictionary - for slightly different get_daily API response
    ---
    dictionary: WEATHER_VALS
    key: (datetime object)
    value: (arr<float>) [temperature (deg F), humidity (%)]
    """
    for item in dictionary:
        items = []
        temp = float(item['temp'][1]['max']['value'])
        humid = float(item['humidity'][0]['min']['value'])
        items.append(temp)
        items.append(humid)
        observation_time = dt.strptime(item['observation_time']['value'], "%Y-%m-%d")
        observation_time = observation_time.replace(tzinfo=pytz.utc)
        WEATHER_VALS[observation_time] = items


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
    nowcast_end = now_time+timedelta(seconds=WEATHER.nowcast_end)
    hourly_end = now_time+timedelta(seconds=WEATHER.hourly_end)
    daily_end = now_time+timedelta(seconds=WEATHER.daily_end-86400)

    # array for fields
    fields = ['temp', 'humidity', 'humidity:%']

    # print(f'total time delta: {total_time_delta} secs')

    # setting relatives to prevent conflict
    relative_start_time = start_time

    # populate weather_data array with nowcast
    if total_time_delta > 0 and start_time < nowcast_end:
        # determine relative bounds
        relative_end_time = min(end_time, nowcast_end)
        # call API
        data = WEATHER.get_nowcast(
            lat, lon, 1, 'us', fields,
            relative_start_time.isoformat(), relative_end_time.isoformat()
        )
        # append data
        clean_data(data)
        # update variables for next timestep
        total_time_delta -= round(
            (relative_end_time-start_time).total_seconds()
        )
        relative_start_time = relative_end_time

    # print(f'after nowcast: {total_time_delta} secs')

    # populate weather_data array with hourly
    if total_time_delta > 0 and relative_start_time < hourly_end:
        # determine relative bounds
        relative_end_time = min(end_time, hourly_end)
        # call API
        data = WEATHER.get_hourly(
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

    # print(f'after hourly: {total_time_delta} secs')

    # populate weather_data array with daily
    if total_time_delta > 0 and relative_start_time < daily_end:
        # determine relative bounds
        relative_end_time = daily_end
        # call API
        data = WEATHER.get_daily(
            lat, lon, 'us', fields,
            relative_start_time.isoformat(), relative_end_time.isoformat()
        )
        # append data
        clean_daily(data)
        # update variables for next timestep
        total_time_delta -= round(
            (relative_end_time-relative_start_time).total_seconds()
        )

    # print(f'after daily: {total_time_delta} secs')

    # make sure data has been logged for the entire time frame
    try:
        assert total_time_delta <= 0
    except AssertionError:
        print("error in time processing.")


def window_slider(lat, lon, start_time, end_time, duration,
                  alpha=-1, beta=1, theta=1.01):
    """
    Iterates through dictionary keys, finds a duration and calculates
    a weighted quantity to determine safest time to go out.
    ---
    duration: (num) seconds
    alpha: (num) weather weight
    beta: (num) humidity weight
    theta: (num) duration weight *** NEED TO PREDETERMINE FOR SPECIFIC RANGES
    """
    # call schedule
    schedule(lat, lon, start_time, end_time, duration)

    # loop variables
    best_start_time = dt.utcnow().replace(tzinfo=pytz.utc)
    best_end_time = dt.utcnow().replace(tzinfo=pytz.utc)
    avg_index = 10**1000
    temp_avg_index = 0
    ctr = 0

    # TODO: Try Memoization to Improve Runtime
    # OPTIMIZE LOW
    # loop through finding durations and keeping running average
    for start_time in WEATHER_VALS:
        for end_time in WEATHER_VALS:
            if start_time == end_time:
                continue
            # compute average
            ctr += 1
            temp_avg_index = (((ctr-1)/ctr)*temp_avg_index+
                              (1/ctr)*(alpha*WEATHER_VALS[end_time][0]+
                               beta*WEATHER_VALS[end_time][1]))
            # if duration is in range
            if duration*theta >= (end_time-start_time).total_seconds() >= duration:
                ctr = 0
                temp_avg_index = 0
                # update if better than last
                if temp_avg_index < avg_index:
                    avg_index = temp_avg_index
                    best_start_time = start_time
                    best_end_time = end_time
                break

    return (best_start_time, best_end_time)

# Testing
# now_time = dt.utcnow().replace(tzinfo=pytz.utc)
# start_time = now_time + timedelta(seconds=100)
# end_time = now_time + timedelta(days=2)
# print(f'start: {start_time}')
# print(f'end: {end_time}')
# print(window_slider(10, 10, start_time, end_time, 1800))
