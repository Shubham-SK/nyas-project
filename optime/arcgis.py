"""
Calls Arcgis API and Obtains Store Location Data
"""
import requests
from instance import config
import urllib

class Arcgis():

    base_url = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?'
    api_key = config.ARCGIS_REST_API_KEY

    def __init__(self):
        pass

    def find_places(self, lat, lon, max_locations, categories):
        """
        """
        # parse categories
        categories = " ".join(map(urllib.parse.quote, categories))

        # construct URL
        url = (
            f'{self.base_url}'
            f'f=json'
            f'&category={categories}'
            f'&location={lat},{lon}'
            f'&outFields=Place_addr,PlaceName'
            f'&maxLocations={max_locations}'
        )
        print(url)
        # get response as JSON
        response = requests.get(url).json()

        return response

# Testing
# https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates/f=json&category=Coffee%20Shop&location=-118.58864,34.06145&outFields=Place_addr,PlaceName&maxLocations=4
# https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates/f=json&category=Coffee Shop&location=-118.58864,34.06145&outFields=Place_addr,PlaceName&maxLocations=4
# https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?f=json&category=Coffee Shop&location=-118.58864,34.06145&outFields=Place_addr, PlaceName&maxLocations=5
# arcgis = Arcgis()
# print(arcgis.find_places(-118.58864, 34.06145, 4, ['Coffee Shop']))
