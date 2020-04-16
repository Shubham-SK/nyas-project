"""
Initialize the Application.
"""
from flask import Flask, request
from scheduling import schedule, window_slider
import climacell
from datetime import datetime, timedelta
import pytz

app = Flask(__name__, static_url_path='/static') # pylint: disable=C0103
# Load third party secret keys
# app.config.from_object('config')
app.config.from_pyfile('instance/config.py')

weather = climacell.Weather()

@app.route('/')
def home():
    return app.send_static_file('index.html'),200

@app.route('/realtime')
def forecast():
    "Get real time updates"
    return str(weather.get_realtime(10, 10, 'si', ['temp', 'temp:F']))

@app.route('/nowcast')
def nowcast():
    "Get updates for a 6 hour range"
    return str(weather.get_nowcast(10, 10, 5, 'si', ['temp', 'temp:F'], "now",
               "2020-04-13T21:30:50Z"))

@app.route('/hourly')
def hourly():
    "Get hourly updates"
    return str(weather.get_hourly(10, 10, 'si', ['temp', 'temp:F'], "now",
               "2020-04-14T21:30:50Z"))

@app.route('/daily')
def daily():
    "Get daily updates"
    return str(weather.get_daily(10, 10, 'si', ['temp', 'temp:F'], "now",
               "2020-04-14T21:30:50Z"))

@app.route('/schedule')
def scheduleTime():
    "Give the best time to go out"
    args = request.args
    # lat, lon, start_time, end_time, duration
    start_time = datetime.strptime(args["start"], '%Y-%m-%d').replace(tzinfo=pytz.utc)
    now = datetime.utcnow().replace(tzinfo=pytz.utc) + timedelta(seconds=10)

    # If the user specified today as the starting date
    if (start_time.strftime('%x') == now.strftime('%x')):
        start_time = now
    end_time = datetime.strptime(args["end"], '%Y-%m-%d').replace(tzinfo=pytz.utc)
    count = args["count"]
    duration = int(args["duration"])
    if (count == "Minutes"):
        duration *= 60
    elif (count == "Hours"):
        duration *= 3600
    elif (count == "Days"):
        duration *= 86400
    lat = args["lat"]
    long = args["long"]
    schedule(lat, long, start_time, end_time, duration)
    bestStartTime, bestEndTime = window_slider(duration)
    return "The best time interval to go out is %s to %s" % (bestStartTime.strftime("%c"), bestEndTime.strftime("%c"))

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8000,debug=True)
