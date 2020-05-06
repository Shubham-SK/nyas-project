import functools
from datetime import datetime, timedelta

import pytz
from bson.objectid import ObjectId
from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)
from pymongo import MongoClient
from tzwhere import tzwhere
from werkzeug.security import check_password_hash, generate_password_hash

from .API.climacell import Weather
from .API.instance.config import SECRET_KEY
from .API.scheduling import schedule, window_slider
from .API.store_filter import get_safest_stores

app = Flask(__name__, static_url_path='/static')  # pylint: disable=C0103
# Load third party secret keys
app.config.from_pyfile('API/instance/config.py')
app.secret_key = SECRET_KEY

weather = Weather()

productStorage = {
    "No record" : -1,
    "1-10" : 10,
    "10-25" : 25,
    "25-40" : 40,
    "40+" : 50}

def login_required(view):
    'Use as a decorator with pages where login is required'
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(**kwargs)

    return wrapped_view


def get_db():
    if 'db' not in g:
        client = MongoClient('mongodb://localhost:27017')
        g.db = client.optime
    return g.db


def get_stores_db():
    if 'db' not in g:
        client = MongoClient('mongodb://localhost:27017')
        g.db = client.optime.allStores
    return g.db


def swap(item, item1):
    """
    Used to swap the time window for scheduling if the user specifies
    an end time that is before the start time
    """
    return (item1, item)


def registerStore(id, lat, lon, product):
    """
    Insert a new store into the databse
    """

    # Product storage: 1-10 = 10, 10-25 = 25, 25-40 = 40, 40+ = 50
    db = get_stores_db()
    db.stores.insert_one(
        {'_id': id,
         'location': [{'lat' : lat}, {'lon' : lon}],
         'stock': [{'name': product, 'stock': -1, 'stockStr': "No record"}],
         'hours': {'open': '00:00', 'close': '00:00'}})


def getAllProducts():
    """
    Get all the products the user wants to buy across all stores
    Returns a 2D array where each subarray represents the user's products for that shopping task
    """

    allProducts = []
    for task in g.user['shoppingTasks']:
        products = []
        for prodDict in task['product']:
            for key, value in prodDict.items():
                products.append(value)
        allProducts.append(products)
    return allProducts

def getAllStores():
    allStores = []
    storeDB = get_stores_db()
    for task in g.user['shoppingTasks']:
        allStores.append(storeDB.stores.find_one(
            {'location': [{'lat' : task['location'][0]}, {'lon' : task['location'][1]}]}))
    return allStores

def constructStore(lat, lon, id, name, storeLat, storeLon, storeAddress, product):
    """
    Construct/return a dictionary representing a shopping task to be inserted in the database
    """

    storeDict = {}
    storeDict['_id'] = id
    storeDict['name'] = name
    storeDict['product'] = [{"productName" : product}]
    storeDict['location'] = [storeLat, storeLon]
    storeDict['storeAddress'] = storeAddress
    storeDict['storeStaticMap'] = "https://maps.googleapis.com/maps/api/staticmap?size=411x275&style=invert_lightness:true&style=feature:road.highway|color:0x808080&path=color:0x1770fb|weight:6|%s,%s|%s,%s&key=AIzaSyC4Kc0Oam47F3Fuznw0nqUWyckCptf_fog" % (lat, lon, storeLat, storeLon)
    storeDict['storeGoogleMap'] = "https://www.google.com/maps/dir/'%s,%s'/'%s'/" % (lat, lon, storeAddress)
    storeDict['selectURL'] = "/selectStore?lat=%s&lon=%s&id=%s&name=%s&storeLat=%s&storeLon=%s&storeAddress=%s&product=%s" % (lat, lon, id, name, storeLat, storeLon, storeAddress, product)

    return storeDict
