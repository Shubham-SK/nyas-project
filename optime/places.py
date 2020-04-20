"""
Calls Google Places API and parses response.
"""
from instance import config
import requests, json

stores = ["Safeway", "Walmart", "Sprouts", "Trader Joes"]

class Stores:
    api_key = config.GOOGLE_API_KEY
    base_url = 'https://maps.googleapis.com/maps/api/place'

    def __init__(self):
        pass

    def find_place(self, input, lat, long, radius, inputtype="textquery"):
        """
        input: (string) store name
        lat: (num)
        long: (num)
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
            f'&locationbias=circle:{radius}@{lat},{long}'
            f'&key={self.api_key}'
        )

        # record response
        response = requests.get(url)
        responseData = json.loads(response.text)

        return responseData

    def get_details(self, place_id):
        """
        place_id = (bs code thing) place_id
        ---
        return: json
        """
        # construct url
        url = (
            f'{self.base_url}/details/json?'
            f'place_id={place_id}'
            f'&fields=opening_hours'
            f'&key={self.api_key}'
        )
        print(url)
        # record response
        response = requests.get(url)
        responseData = json.loads(response.text)

        return responseData

# Test code
# store = Stores()
# store.find_place("Safeway", 37.710079, -121.927002, 80467)
# print(store.get_details('ChIJQwOmU2zsj4ARL1OEw9L_v4Y'))
