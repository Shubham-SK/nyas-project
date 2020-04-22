"""
Calls Google Places API and parses response.
"""
from instance import config
import requests, json


class Stores:
    api_key = config.TOMTOM_API_KEY
    base_url = 'https://api.tomtom.com/search/2'
    stores = ["Safeway", "Walmart", "Sprouts", "Trader Joes"]

    def __init__(self):
        pass

    def find_place(self, lat, lon, radius):
        """
        input: (string) store name
        lat: (num)
        lon: (num)
        radius: (num) meters
        ---
        return: json
        """
        # construct URL
        url = (
            f'{self.base_url}/nearbySearch/.JSON?'
            f'key={self.api_key}'
            f'&lat={lat}'
            f'&lon={lon}'
            f'&radius={radius}'
            f'&openingHours=nextSevenDays'
        )

        # record response
        response = requests.get(url).json()

        return response

    def get_details(self, place_id):
        """
        place_id = (google place code) place_id
        ---
        return: json
        """
        # construct url
        url = (
            f'{self.base_url}/details/json?'
            f'place_id={place_id}'
            # f'&fields=opening_hours'
            f'&key={self.api_key}'
        )

        # record response
        response = requests.get(url).json()

        return response

# Testing
# store = Stores()
# print(store.find_place(37.710079, -121.927002, 30))
#print(store.get_details('ChIJQwOmU2zsj4ARL1OEw9L_v4Y'))
