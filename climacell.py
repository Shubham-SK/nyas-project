"""
Calls the ClimaCell Weather API & Obtains Forecast Data.
"""
import urllib
import requests
from instance import config

class Weather:
    """
    Functions for various API calls
    """
    base_url = "https://api.climacell.co/v3"
    api_key = config.CLIMACELL_API_KEY

    def __init__(self):
        pass

    def get_realtime(self, lat, lon, unit_system, fields):
        """
        real time minutely updates for present time
        location_id: (str) ID of previously defined location
        lat: (num) -59.9, 59.9
        lon: (num) -180, 180
        unit_system: (str) 'si' or 'us'
        fields: (arr<str>) desired stats
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
        print(response)

        return response

    # def get_nowcast(self):
    #     pass
    #
    # def get_hourly(self):
    #     pass
    #
    # def get_daily(self):
    #     pass

# Testing
# weather = Weather()
# weather.get_realtime
# (lat=10, lon=10, unit_system='si', fields=['temp', 'temp:F'])
