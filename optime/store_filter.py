"""
Uses API data from Google and NYTimes to find the safest stores
"""
from corona import Cases
from arcgis import Arcgis
from uszipcode import SearchEngine

STORES = Arcgis()
CASES = Cases()

def clean_store_data(raw_json):
    """
    Parse the JSON return from arcgis calls
    ---
    raw_json: (json) response
    ---
    return: arr<name, [lat, lon], address>
    """
    cleaned_store_data = []

    # iterate through stores and record place_id, address
    for store in raw_json['candidates']:
        name = store['address']
        location = [store['location']['y'], store['location']['x']]
        address = store['attributes']['Place_addr']
        cleaned_store_data.append([name, location, address])

    return cleaned_store_data


def order(store):
    """
    Lambda quantifier
    ---
    store: (arr) cleaned
    ---
    return: (num) death + cases
    """
    # extract location data
    address = store[2].split(", ")
    zip = address[3]
    state = address[2]

    # lookup county
    search = SearchEngine(simple_zipcode=True)
    county = search.by_zipcode(zip).to_dict()['county']

    # invalid names
    if ' County' in county:
        county = county.replace(' County','')

    if county == "New York":
        county = "New York City"

    cases = CASES.get_cases(county, state)
    cases = int(cases[0][4])+int(cases[0][5])

    return cases


def get_safest_stores(lat, lon, max_locations, k, categories):
    """
    Find top-k safest stores using case data.
    ---
    lat: (num) -59.9, 59.9
    lon: (num) -180, 180
    max_locations: (num) number of suggested stores
    categories: (arr<str>) lookup fields
    k: (num) number of top safest
    ---
    return: arr<cleaned> top-k safest stores
    """
    # make sure paramters are valid
    try:
        assert k <= max_locations
    except AssertionError:
        print(f'invalid parameters provided.')

    # iterate finding closest stores
    store_info = STORES.find_places(lat, lon, max_locations, categories)
    store_info = clean_store_data(store_info)

    # TODO: ADD THE SIR MODEL IN CORONA.PY, FIND POPULATION DATA W FIPS

    # sort by cases for each address
    # store_info = sorted(store_info, key=order)

    return store_info[:k]

# Testing
# print(get_safest_stores(37.710079, -121.927002, 15, 5, ['Grocery']))
