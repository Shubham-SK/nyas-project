"""
Calls Google Places API and parses response.
"""
from instance import config
import requests, json


class Stores:
    api_key = config.GOOGLE_API_KEY
    base_url = 'https://maps.googleapis.com/maps/api/place'
    stores = ["Safeway", "Walmart", "Sprouts", "Trader Joes"]

    def __init__(self):
        pass

    def find_place(self, input, lat, lon, radius, inputtype="textquery"):
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
            f'{self.base_url}/findplacefromtext/json?'
            f'input={input}'
            f'&inputtype={inputtype}'
            f'&fields=place_id,formatted_address'
            f'&locationbias=circle:{radius}@{lat},{lon}'
            f'&key={self.api_key}'
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
# print(store.find_place("Trader Joes", 37.710079, -121.927002, 10000000))
#print(store.get_details('ChIJQwOmU2zsj4ARL1OEw9L_v4Y'))
