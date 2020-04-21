"""
Uses API data from Google and NYTimes to find the safest stores
"""
from corona import Cases
from places import Stores

STORES = Stores()
CASES = Cases()

def clean_store_data(name, raw_json):
    cleaned_store_data = []

    # iterate through stores and record place_id, address
    for store in raw_json['candidates']:
        address = store['formatted_address']
        place_id = store['place_id']
        cleaned_store_data.append([name, address, place_id])

    return cleaned_store_data


def clean_case_data(raw_json):
    pass


def get_safest_stores(lat, lon, radius):
    store_list = []

    # iterate finding closest stores
    for store in STORES.stores:
        store_info = STORES.find_place(store, lat, lon, radius)
        store_info = clean_store_data(store, store_info)
        store_list.append(store_info)

    # TODO: ADD THE SIR MODEL IN CORONA.PY, FIND POPULATION DATA W FIPS

    return store_list

# Testing
# print(get_safest_stores(37.710079, -121.927002, 10000))
