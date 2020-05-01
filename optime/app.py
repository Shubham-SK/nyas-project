"""
Initialize the Application.
"""
import functools
import re
from datetime import datetime, timedelta

import pytz
from bson.objectid import ObjectId
from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)
from pymongo import MongoClient
from tzwhere import tzwhere
from werkzeug.security import check_password_hash, generate_password_hash

import climacell
from instance.config import SECRET_KEY
from scheduling import schedule, window_slider
from store_filter import get_safest_stores

app = Flask(__name__, static_url_path='/static')  # pylint: disable=C0103
# Load third party secret keys
# app.config.from_object('config')
app.config.from_pyfile('instance/config.py')
app.secret_key = SECRET_KEY

weather = climacell.Weather()

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
            # parsed_url = urllib.parse.urlparse(url_for("login"))
            # query = urllib.parse.parse_qs(parsed_url.query)
            # query["next"] = request.url
            # query_string = urllib.parse.urlencode(query)
            # new_url = urllib.parse.urlunparse(
            #     (parsed_url.scheme, parsed_url.netloc, parsed_url.path,
            #      parsed_url.params, query_string, parsed_url.fragment)
            # )

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
    return (item1, item)


def registerStore(id, lat, lon, product):
    # Product storage: 1-10 = 10, 10-25 = 25, 25-40 = 40, 40+ = 50
    db = get_stores_db()
    db.stores.insert_one(
        {'_id': id,
         'location': [{'lat' : lat}, {'lon' : lon}],
         'stock': [{'name': product, 'stock': -1, 'stockStr': "No record"}],
         'hours': {'open': '00:00', 'close': '00:00'}})
    print("\n\nINSERTING STORE\n%s\n\n" % (db.stores.find_one({"_id": id})))

def getAllProducts():
    allProducts = []
    for task in g.user['shoppingTasks']:
        products = []
        for prodDict in task['product']:
            for key, value in prodDict.items():
                products.append(value)
        allProducts.append(products)
    return allProducts

def constructStore(lat, lon, id, name, storeLat, storeLon, storeAddress, product):
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


@app.route('/scheduling', methods=['GET', 'POST'])
@login_required
def scheduling():
    'Give the best time to go out'
    if request.method == 'POST':
        args = request.form

        # lat, lon, start_time, end_time, duration
        lat = g.user['lat']
        lon = g.user['lon']

        # finding timezone
        tz = tzwhere.tzwhere(forceTZ=True)
        local = tz.tzNameAt(float(lat), float(lon), forceTZ=True)

        # local start time
        start_time_local = datetime.strptime(args['start'],
                                             '%Y-%m-%d').replace(tzinfo=pytz.timezone(local))
        now_time_local = datetime.now(pytz.timezone(local))
        print("\n\n START TIME LOCAL: %s\n\n" % (start_time_local.strftime('%c')))
        print("\n\n NOW TIME LOCAL: %s\n\n" % (now_time_local.strftime('%c')))

        # if the user specified today as the starting date
        if start_time_local < now_time_local:
            start_time_utc = (datetime.utcnow().replace(tzinfo=pytz.utc) +
                              timedelta(seconds=10))
        else:
            start_time_utc = start_time_local.astimezone(pytz.utc)

        # local end time
        end_time_local = datetime.strptime(args['end'],
                                           '%Y-%m-%d').replace(tzinfo=pytz.timezone(local))
        end_time_utc = end_time_local.astimezone(pytz.utc)

        if (end_time_utc < start_time_utc):
            (start_time_utc, end_time_utc) = swap(start_time_utc, end_time_utc)
            (start_time_local, end_time_local) = swap(
                start_time_local, end_time_local)
        print("\n\n START TIME UTC: %s\n\n" % (start_time_utc.strftime('%c')))
        print("\n\n END TIME UTC: %s\n\n" % (end_time_utc.strftime('%c')))
        # print(f'utc times: {start_time_utc} {end_time_utc}')
        # print(f'local times: {start_time_local} {end_time_local}')

        count = args['count']
        duration = int(args['duration'])
        name = args['name']

        if count == 'Minutes':
            duration *= 60
        elif count == 'Hours':
            duration *= 3600
        elif count == 'Days':
            duration *= 86400

        bestStartTime, bestEndTime = window_slider(lat, lon, start_time_utc,
                                                   end_time_utc, duration)

        # bestStartTime = bestStartTime.strftime('%c')
        # bestEndTime = bestEndTime.strftime('%c')

        bestStartTime = bestStartTime.astimezone(pytz.timezone(local))
        bestEndTime = bestEndTime.astimezone(pytz.timezone(local))

        task = {
            "_id": ObjectId(),
            "name": name,
            "start_time": bestStartTime,
            "end_time": bestEndTime,
        }

        db = get_db()
        db.users.update_one({"_id": g.user["_id"]}, {
            "$push": {"items": task}})

        return redirect(url_for('scheduling'))
        # print("insertion", g.user['items'])

    return render_template('scheduling.html', tasks=g.user['items']), 200


@app.route('/scheduling/delete_task')
def delete_task():
    args = request.args
    task_index = int(args['task_index'])
    db = get_db()
    task_id = g.user["items"][task_index]["_id"]
    db.users.update_one({"_id": g.user["_id"]},
                        {"$pull": {"items": {"_id": task_id}}})
    if ('tasks' in args):
        return redirect("/#personal-tasks")
    return redirect(url_for('scheduling'))


@app.route('/index')
@app.route('/')
def index():
    if g.user is None:
        return render_template('index.html')
    else:
        return render_template('tasks.html', tasks=g.user['items'],
                               shoppingTasks=g.user['shoppingTasks'],
                               number=g.user['phone_number'],
                               lentasks=len(g.user['items']),
                               allProducts=getAllProducts(),
                               lenshoppingtasks=len(g.user['shoppingTasks']))  # , userLat=g.user["lat"], userLon=g.user["lon"])


@app.route('/shopping', methods=['GET', 'POST'])
@login_required
def shopping(task_storename=None, task_storeaddr=None, task_lat=None, task_lon=None, task_userProds=None):
    print('Getting request for stores')
    # lat, lon, max_locations, k, categories, product
    lat = g.user['lat']
    lon = g.user['lon']
    max_locations = 20
    k = 3
    categories = ['Grocery']
    product = None
    allStores = []
    storeDB = get_stores_db()
    task_product = {}

    if request.method == 'POST':
        args = request.form
        categories = args.getlist('category')
        product = args['product']
        print(args)
        for i in range(len(categories)):
            if (categories[i] == "Grocery Store"):
                categories[i] = "Grocery"
    elif 'task_storename' in request.args:
        task_storename = request.args['task_storename']
        task_storeaddr = request.args['task_storeaddr']
        task_lat = request.args['task_lat']
        task_lon = request.args['task_lon']
        task_userProds = request.args.getlist('task_userProds')

        task_product = storeDB.stores.find_one(
            {'location': [{'lat' : task_lat}, {'lon' : task_lon}]})
        print("\n\nUSER PRODUCTS:\n%s\n\n" % (task_product))
    if 'update' in request.args:
        update = 'true'
        print('oren', request.args['update'])
    else:
        update = 'false'

    # ['Walmart', [37.72945007660575, -121.92957003664371], '9100 Alcosta Blvd, San Ramon, California, 94583']
    storesArr = get_safest_stores(lat, lon, max_locations, k, categories)

    for store in storesArr:
        storeLat = str(store[1][0])
        storeLon = str(store[1][1])
        allStores.append(constructStore(lat, lon, ObjectId(), store[0], storeLat, storeLon, store[2], product))

    allProducts = getAllProducts()
    # print("\n\nALLPRODUCTS\n%s\n\n"%(allProducts))
    return render_template('shopping.html', userLat=lat, userLon=lon,
    shoppingTasks=g.user['shoppingTasks'], allProducts=allProducts,
    storeLocs=allStores, req=request.method,
    task_storename=task_storename,task_storeaddr=task_storeaddr,
    task_userProds=task_userProds,task_product=task_product,
    task_lat=task_lat,task_lon=task_lon, product=product, update=update), 200


@app.route('/selectStore')
def selectStore():
    params = []
    for i in request.args:
        params.append(request.args[i])
        # print(request.args[i])
    # print("\n\nstore request received. ID=%s\n\n" % (params))
    allLocs = [list(task.values())[3] for task in g.user['shoppingTasks']]
    print("\n\nstore request received. allLocs=%s\n\n" % (allLocs))
    lat, lon, id, name, storeLat, storeLon, storeAddress, product = params
    store = constructStore(lat, lon, id, name, storeLat, storeLon, storeAddress, product)
    newProduct = store.pop("product")[0]

    db = get_db()
    storeDB = get_stores_db()

    # print("\n\nnewProduct\n%s" % (newProduct))
    # print(store)
    # print("\n\n")
    if ([storeLat, storeLon] not in allLocs):
        db.users.update_one({"_id": g.user["_id"]},
        {"$push": {"shoppingTasks": constructStore(lat, lon, id, name, storeLat, storeLon, storeAddress, product)}})
    else:
        db.users.update_one(
            {"_id": g.user["_id"]},
            {"$addToSet" : { "shoppingTasks.$[elem].product" : newProduct }},
            upsert=True,
            array_filters=[ {"elem.location" : [storeLat,storeLon]}]
        )
    print("\n\nTASK ADDED\n%s\n\n" % (g.user))

    storeVal = storeDB.stores.find_one(
        {'location': [{'lat' : storeLat}, {'lon' : storeLon}]})
    if (storeVal == None):
        # print("\n\nNEW STORE\n\n")
        # print(g.user)
        # print("\n\n")
        registerStore(ObjectId(), storeLat, storeLon, product)
        print("\n\nNEW STORE ADDED\n%s\n\n" % (storeDB.stores.find_one(
            {'location': [{'lat' : storeLat}, {'lon' : storeLon}]})))

    else:
        # print("UPDATING PRODUCTS")
        storeDB.stores.update_one(
            {'location': [{'lat' : storeLat}, {'lon' : storeLon}], 'stock.name': {'$ne': newProduct["productName"]}},
            {"$addToSet" : {"stock": {'name': newProduct["productName"], 'stock': -1, 'stockStr': "No record"}}}
        )

        # storeDB.stores.update_one(
        #     {'location': [{'lat' : storeLat}, {'lon' : storeLon}]},
        #     {"$addToSet" : {"stock": {'$elem.name': product, 'stock': 0, 'stockStr': "0"}}},
        #     upsert=True,
        #     array_filters=[ {"elem.name" : product}]
        # )
        print("\n\nPRODUCT ADDED TO STORE\n%s\n\n" % (storeDB.stores.find_one(
            {'location': [{'lat' : storeLat}, {'lon' : storeLon}]})))

    # print("\n\nSHOPPING TASK ADDED\n\n")
    # print(g.user)
    # print("\n\n\n\n\n\n\n\n\n\n\n\n")

    return redirect(url_for('shopping'))

@app.route('/shopping/refresh')
def refreshProdSelections():
    args = request.args

    storeName = args['name']
    storeLat = args['lat']
    storeLon = args['lon']
    task_userProds = []
    task_storeaddr = ""

    # task_storename=None, task_storeaddr=None, task_lat=None, task_lon=None, task_userProds=None

    for t in g.user['shoppingTasks']:
        if (t['location'] == [storeLat, storeLon]):
            task_userProds = [item["productName"] for item in t["product"]]
            task_storeaddr = t['storeAddress']
    print("REQUEST TO CHANGE STORE RECEIVED: %s" % (task_userProds))
    return redirect(url_for('.shopping',task_storename=storeName,task_storeaddr=task_storeaddr, task_userProds=task_userProds, task_lat=storeLat, task_lon=storeLon))

@app.route('/shopping/delete_task')
def delete_shoppingTask():
    args = request.args
    task_index = int(args['task_index'])
    db = get_db()
    task = g.user["shoppingTasks"][task_index]
    task_userProds = [item["productName"] for item in task["product"]]
    print("\n\nDELETED TASK:%s\n\n" % (task))
    task_id = task["_id"]
    db.users.update_one({"_id": g.user["_id"]},
                        {"$pull": {"shoppingTasks": {"_id": task_id}}})
    if ('tasks' in args):
        print("\n\nTask:%s\n\n"%(task))
        return redirect(url_for('.shopping',task_storename=task['name'],task_storeaddr=task['storeAddress'], task_userProds=task_userProds, task_lat=task['location'][0], task_lon=task['location'][1], update="true"))
    return redirect(url_for('shopping'))

@app.route('/update')
def updateStore():
    args = request.args.to_dict()
    # The minimum number of parameters is 1 (the store name)
    if (len(args) > 1):
        location = [{'lat' : args['lat']}, {'lon' : args['lon']}]
        # [:5] to always store 'HH:MM' instead of 'HH:MM:00'
        hours = {'open': args['open'][:5], 'close': args['close'][:5]}
        args.pop('lat')
        args.pop('lon')
        args.pop('open')
        args.pop('close')
        args.pop('category')

        newStocks = []
        for stock in args:
            if (args[stock] == ''):
                args[stock] = "No record"
            print("\n\nStock: %s\n\n" % (stock.split(':')))
            newStocks.append({'name':stock.split(':')[1], 'stock':productStorage[args[stock]], 'stockStr': args[stock]})

        storeDB = get_stores_db()
        storeDB.stores.update_one({"location": location}, {
                            "$set": {"hours": hours, "stock": newStocks}})
        print("\n\nNEW STORE DATA\n%s\n\n" % (storeDB.stores.find_one(
            {'location': location})))
    return redirect(url_for('shopping'))

@app.route('/update_settings', methods=("POST",))
@login_required
def update_settings():
    phone_number = request.form.get("phone_number")
    if phone_number is None:
        return "No phone number given"
    else:
        phone_number = "".join(char for char in phone_number)

        if len(phone_number) != 10 or not phone_number.isdigit():
            return "phone number is invalid"

        db = get_db()
        db.users.update_one({"_id": g.user["_id"]}, {
                            "$set": {"phone_number": phone_number}})
        return redirect(url_for('index'))


@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        print('Getting post request for register')
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        lat = request.form['lat']
        lon = request.form['lon']

        db = get_db()

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif db.users.find_one({'email': email}):
            error = 'A user with that email is already registered'
        elif db.users.find_one({'username': username}):
            error = 'A user with username {} is already registered.'.format(
                username)

        if error is None:
            password_hash = generate_password_hash(password)
            db.users.insert_one(
                {'username': username,
                 'email': email,
                 'lat': lat,
                 'lon': lon,
                 'password': password_hash,
                 'items': [],
                 'shoppingTasks': [],
                 'phone_number': ''})
            return redirect(url_for('login'))
        else:
            print(error)

    return render_template('register.html', error=error)


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    print('Getting request for login')
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        db = get_db()
        print(db)
        print(f"lat lon {lat} {lon}")

        user = db.users.find_one({'email': email})
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        elif lat is "" or lon is "":
            error = 'Please allow location access'
            # print("NEW LAT:", lat)
            # print("NEW LON:", lon)
        if error is None:
            session.clear()
            session['user_id'] = str(user['_id'])
            session['location'] = (lat, lon)
            newLat = {"$set": {"lat": lat}}
            newLon = {"$set": {"lon": lon}}
            db.users.update_one({'email': email}, newLat)
            db.users.update_one({'email': email}, newLon)

            # print(db.users)
            if "next" in request.args:
                return redirect(request.args["next"])
            else:
                return redirect(url_for('index'))

        flash(error)

    next_url = request.args.get('next')
    if next_url is not None:
        form_action = url_for('login', next=next_url)
    else:
        form_action = url_for('login')
    return (render_template('login.html', error=error,
                            form_action=form_action),
            200)


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().users.find_one({"_id": ObjectId(user_id)})
        print("Logged in user")


@app.route('/auth/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
