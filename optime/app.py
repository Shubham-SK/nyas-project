"""
Initialize the Application.
"""
import pytz
from datetime import datetime, timedelta
import climacell
from flask import (
    Flask, request, url_for, g, redirect, render_template, flash, session,
)
import functools
from werkzeug.security import check_password_hash, generate_password_hash
from scheduling import schedule, window_slider
from pymongo import MongoClient

app = Flask(__name__, static_url_path='/static')  # pylint: disable=C0103
# Load third party secret keys
# app.config.from_object('config')
app.config.from_pyfile('instance/config.py')

weather = climacell.Weather()


def login_required(view):
    "Use as a decorator with pages where login is required"
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def get_db():
    if 'db' not in g:
        client = MongoClient('mongodb://localhost:27017')
        g.db = client.users
    return g.db


@app.route('/')
def index():
    return app.send_static_file('index.html'), 200


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


@app.route('/schedule')
def scheduleTime():
    'Give the best time to go out'
    args = request.args

    # lat, lon, start_time, end_time, duration
    start_time = datetime.strptime(
        args['start'], '%Y-%m-%d').replace(tzinfo=pytz.utc)
    now = datetime.utcnow().replace(tzinfo=pytz.utc) + timedelta(seconds=10)

    # If the user specified today as the starting date
    if start_time.strftime('%x') == now.strftime('%x'):
        start_time = now

    end_time = datetime.strptime(
        args['end'], '%Y-%m-%d').replace(tzinfo=pytz.utc)
    count = args['count']
    duration = int(args['duration'])

    if count == 'Minutes':
        duration *= 60
    elif count == 'Hours':
        duration *= 3600
    elif count == 'Days':
        duration *= 86400

    lat = args['lat']
    lon = args['lon']

    bestStartTime, bestEndTime = window_slider(lat, lon, start_time,
                                               end_time, duration)
    bestStartTime = bestStartTime.strftime('%c')
    bestEndTime = bestEndTime.strftime('%c')

    return f'{bestStartTime} to {bestEndTime}'


@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.find_one({"username": username}):
            error = 'User {} is already registered.'.format(username)

        if error is None:
            password_hash = generate_password_hash(password)
            db.insert_one({"username": username, "password": password_hash})
            return redirect(url_for('login'))

        flash(error)

    return render_template('register.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    '''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.find_one({"username": username})

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)
    '''
    return app.send_static_file('login.html')
    #return render_template('rendertest.html')


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().find_one({"username": user_id})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)
