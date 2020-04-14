"""
Calls the ClimaCell Weather API & Obtains Forecast Data.
"""
import urllib
import requests
import flask
#from optime.instance import config
from instance import config

class Weather:
    """
    Functions for various API calls
    ---
    get_realtime
    get_nowcast
    get_hourly
    get_daily
    """
    base_url = "https://api.climacell.co/v3"
    api_key = config.CLIMACELL_API_KEY

    def __init__(self):
        pass

    def get_realtime(self, lat, lon, unit_system, fields):
        """
        Real time minutely updates for present time.
        ---
        location_id: (str) ID of previously defined location
        lat: (num) -59.9, 59.9
        lon: (num) -180, 180
        unit_system: (str) 'si' or 'us'
        fields: (arr<str>) desired stats
        ---
        return: (dict) key: desired stats. value: stat
        """
        # URL encode fields array
        fields = ",".join(map(urllib.parse.quote, fields))

        # construct URL
        url = (
        f'{self.base_url}/weather/realtime?'
        f'lat={lat}l&lon={lon}'
        f'&unit_system={unit_system}'
        f'&fields={fields}'
        f'&apikey={self.api_key}'
        )

        # get response as JSON
        response = requests.get(url).json()

        return response

    def get_nowcast(self, lat, lon, timestep, unit_system, fields,
                    start_time, end_time):
        """
        Minutely updates for 6 hour range in US, 3 hour range
        in Europe and Japan.
        ---
        location_id: (str) ID of previously defined location
        timestep: (num) 1, 60
        lat: (num) -59.9, 59.9
        lon: (num) -180, 180
        unit_system: (str) 'si' or 'us'
        fields: (arr<str>) desired stats
        start_time: (ISO 8601 time stamp) ex: 2019-03-20T14:09:50Z
        end_time: (ISO 8601 time stamp) ex: 2019-03-20T14:09:50Z
        ---
        return: (dict) key: desired stats. value: stat
        """

        # URL encode fields array, end_time and start_time
        fields = ",".join(map(urllib.parse.quote, fields))
        start_time = urllib.parse.quote(start_time)
        end_time = urllib.parse.quote(end_time)

        # construct URL
        url = (
        f'{self.base_url}/weather/nowcast?'
        f'lat={lat}l&lon={lon}'
        f'timestep={timestep}'
        f'&unit_system={unit_system}'
        f'&fields={fields}'
        f'&start_time={start_time}'
        f'&end_time={end_time}'
        f'&apikey={self.api_key}'
        )

        # get response as JSON
        response = requests.get(url).json()

        return response

    def get_hourly(self, lat, lon, unit_system, fields,
                    start_time, end_time):
        """
        Hourly updates for global forecast up to 96 hours.
        ---
        location_id: (str) ID of previously defined location
        lat: (num) -59.9, 59.9
        lon: (num) -180, 180
        unit_system: (str) 'si' or 'us'
        fields: (arr<str>) desired stats
        start_time: (ISO 8601 time stamp) ex: 2019-03-20T14:09:50Z
        end_time: (ISO 8601 time stamp) ex: 2019-03-20T14:09:50Z
        ---
        return: (dict) key: desired stats. value: stat
        """

        # URL encode fields array, end_time and start_time
        fields = ",".join(map(urllib.parse.quote, fields))
        start_time = urllib.parse.quote(start_time)
        end_time = urllib.parse.quote(end_time)

        # construct URL
        url = (
        f'{self.base_url}/weather/forecast/hourly?'
        f'lat={lat}l&lon={lon}'
        f'&unit_system={unit_system}'
        f'&fields={fields}'
        f'&start_time={start_time}'
        f'&end_time={end_time}'
        f'&apikey={self.api_key}'
        )

        # get response as JSON
        response = requests.get(url).json()

        return response

    def get_daily(self, lat, lon, unit_system, fields,
                    start_time, end_time):
        """
        Daily updates for global forecast up to 15 days.
        ---
        location_id: (str) ID of previously defined location
        lat: (num) -59.9, 59.9
        lon: (num) -180, 180
        unit_system: (str) 'si' or 'us'
        fields: (arr<str>) desired stats
        start_time: (ISO 8601 time stamp) ex: 2019-03-20T14:09:50Z
        end_time: (ISO 8601 time stamp) ex: 2019-03-20T14:09:50Z
        ---
        return: (dict) key: desired stats. value: stat
        """

        # URL encode fields array, end_time and start_time
        fields = ",".join(map(urllib.parse.quote, fields))
        start_time = urllib.parse.quote(start_time)
        end_time = urllib.parse.quote(end_time)

        # construct URL
        url = (
        f'{self.base_url}/weather/forecast/daily?'
        f'lat={lat}l&lon={lon}'
        f'&start_time={start_time}'
        f'&end_time={end_time}'
        f'&unit_system={unit_system}'
        f'&fields={fields}'
        f'&apikey={self.api_key}'
        )

        print(url)

        # get response as JSON
        response = requests.get(url).json()
        print(response)

        return response
