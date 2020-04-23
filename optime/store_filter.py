"""
Uses API data from Google and NYTimes to find the safest stores
"""
from corona import Cases
from arcgis import Arcgis

STORES = Arcgis()
CASES = Cases()

def clean_store_data(raw_json):
    """
    raw_json
    """
    cleaned_store_data = []

    # iterate through stores and record place_id, address
    for store in raw_json['candidates']:
        print(store)
        cleaned_store_data.append(store)

    return cleaned_store_data


def clean_case_data(raw_json):
    pass


def get_safest_stores(lat, lon, max_locations, categories):

    # iterate finding closest stores
    store_json = STORES.find_places(lat, lon, max_locations, categories)
    store_info = clean_store_data(store_json)

    # TODO: ADD THE SIR MODEL IN CORONA.PY, FIND POPULATION DATA W FIPS

    return store_info

# Testing
get_safest_stores(37.710079, -121.927002, 3, ['Grocery'])
