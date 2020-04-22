'''
Initialize the Application.
'''
import functools
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


@app.route('/realtime')
def forecast():
    'Get real time updates'
    return str(weather.get_realtime(10, 10, 'si', ['temp', 'temp:F']))


@app.route('/nowcast')
def nowcast():
    'Get updates for a 6 hour range'
    return str(weather.get_nowcast(10, 10, 5, 'si', ['temp', 'temp:F'], 'now',
                                   '2020-04-13T21:30:50Z'))


@app.route('/hourly')
def hourly():
    'Get hourly updates'
    return str(weather.get_hourly(10, 10, 'si', ['temp', 'temp:F'], 'now',
                                  '2020-04-14T21:30:50Z'))


@app.route('/daily')
def daily():
    'Get daily updates'
    return str(weather.get_daily(10, 10, 'si', ['temp', 'temp:F'], 'now',
                                 '2020-04-14T21:30:50Z'))


@app.route('/scheduling/schedule')
@login_required
def schedule_create():
    'Give the best time to go out'
    args = request.args

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
    db.users.update_one({"_id": ObjectId(g.user["_id"])}, {
        "$push": {"items": task}})
    print("insertion", g.user['items'])

    return redirect(url_for('scheduling'))


@app.route('/scheduling/delete_task/<int:task_index>')
def delete_task(task_index):
    db = get_db()
    task_id = g.user["items"][task_index]["_id"]
    db.users.update_one({"_id": g.user["_id"]},
                        {"$pull": {"items": {"_id": task_id}}})
    return redirect(url_for('scheduling'))


@app.route('/index')
@app.route('/')
def index():
    print(g.user)
    return render_template('index.html')


@app.route('/tasks')
@login_required
def tasks():
    return render_template('tasks.html')


@app.route('/shopping')
@login_required
def shopping():
    return render_template('shopping.html'), 200


@app.route('/scheduling')
@login_required
def scheduling():
    return render_template('scheduling.html', tasks=g.user['items']), 200


@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print('Getting post request for register')
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif db.users.find_one({'username': username}):
            error = 'User {} is already registered.'.format(username)

        if error is None:
            password_hash = generate_password_hash(password)
            db.users.insert_one(
                {'username': username,
                 'email': email,
                 'password': password_hash,
                 'items': []})
            return redirect(url_for('login'))
        else:
            print(error)

        flash(error)

    return render_template('register.html')


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    print('Getting request for login')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.users.find_one({'email': email})
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        if error is None:
            session.clear()
            session['user_id'] = str(user['_id'])
            if "next" in request.args:
                return redirect(request.args["next"])
            else:
                return redirect(url_for('scheduling'))
        flash(error)
    next_url = request.args.get('next')
    if next_url is not None:
        form_action = url_for('login', next=next_url)
    else:
        form_action = url_for('login')
    return render_template('login.html', form_action=form_action), 200
    # return render_template('rendertest.html')


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
    app.run(host='localhost', port=5000, debug=True)
