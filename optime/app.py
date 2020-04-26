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


def swap(item, item1):
    return (item1, item)


@app.route('/scheduling', methods=['GET', 'POST'])
@login_required
def scheduling():
    'Give the best time to go out'
    if request.method == 'POST':
        args = request.form

        # lat, lon, start_time, end_time, duration
        lat = args['lat']
        lon = args['lon']

        # finding timezone
        tz = tzwhere.tzwhere(forceTZ=True)
        local = tz.tzNameAt(float(lat), float(lon), forceTZ=True)

        # local start time
        start_time_local = datetime.strptime(args['start'],
                                             '%Y-%m-%d').astimezone(pytz.timezone(local))
        now_time_local = datetime.now(pytz.timezone(local))

        # if the user specified today as the starting date
        if start_time_local.strftime('%x') == now_time_local.strftime('%x'):
            start_time_utc = (datetime.utcnow().replace(tzinfo=pytz.utc) +
                              timedelta(seconds=10))
        else:
            start_time_utc = start_time_local.astimezone(pytz.utc)

        # local end time
        end_time_local = datetime.strptime(args['end'],
                                           '%Y-%m-%d').astimezone(pytz.timezone(local))
        end_time_utc = end_time_local.astimezone(pytz.utc)

        if (end_time_utc < start_time_utc):
            (start_time_utc, end_time_utc) = swap(start_time_utc, end_time_utc)
            (start_time_local, end_time_local) = swap(
                start_time_local, end_time_local)

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


@app.route('/scheduling/delete_task/<int:task_index>')
def delete_task(task_index):
    db = get_db()
    task_id = g.user["items"][task_index]["_id"]
    db.users.update_one({"_id": g.user["_id"]},
                        {"$pull": {"items": {"_id": task_id}}})
    print("DATABASE: ", g.user)
    return redirect(url_for('scheduling'))


@app.route('/index')
@app.route('/')
def index():
    if g.user is None:
        return render_template('index.html')
    else:
        return render_template('tasks.html', tasks=g.user['items'],
                               number=g.user['phone_number'],
                               lentasks=len(g.user['items']),
                               lenshoppingtasks=len(g.user['items']))  # , userLat=g.user["lat"], userLon=g.user["lon"])


@app.route('/shopping', methods=['GET', 'POST'])
@login_required
def shopping():
    print('Getting request for stores')
    # lat, lon, max_locations, k, categories, product
    lat = g.user['lat']
    lon = g.user['lon']
    max_locations = 20
    k = 3
    categories = ['Grocery']
    if request.method == 'POST':
        args = request.form
        categories = args.getlist('category')
        print(args)
        for i in range(len(categories)):
            if (categories[i] == "Grocery Store"):
                categories[i] = "Grocery"
    # ['Walmart', [37.72945007660575, -121.92957003664371], '9100 Alcosta Blvd, San Ramon, California, 94583']
    storesArr = get_safest_stores(lat, lon, max_locations, k, categories)

    allStores = []

    for store in storesArr:
        storeDict = {}
        storeDict['name'] = store[0]
        storeDict['storeLat'] = str(store[1][0])
        storeDict['storeLon'] = str(store[1][1])
        storeDict['storeAddress'] = store[2]
        storeDict['storeStaticMap'] = "https://maps.googleapis.com/maps/api/staticmap?size=411x275&style=invert_lightness:true&style=feature:road.highway|color:0x808080&path=color:0x1770fb|weight:6|%s,%s|%s,%s&key=AIzaSyC4Kc0Oam47F3Fuznw0nqUWyckCptf_fog" % (
            lat, lon, storeDict['storeLat'], storeDict['storeLon'])
        storeDict['storeGoogleMap'] = "https://www.google.com/maps/dir/'%s,%s'/'%s,%s'/" % (
            lat, lon, storeDict['storeLat'], storeDict['storeLon'])

        allStores.append(storeDict)
    return render_template('shopping.html', userLat=lat, userLon=lon, storeLocs=allStores), 200


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

        user = db.users.find_one({'email': email})
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        elif lat is "" or lon is "":
            error = 'No location provided'
        if error is None:
            session.clear()
            session['user_id'] = str(user['_id'])
            session['location'] = (lat, lon)
            newLat = {"$set": {"lat": lat}}
            newLon = {"$set": {"lon": lon}}
            # print("NEW LAT:", newLat)
            # print("NEW LON:", newLon)
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
