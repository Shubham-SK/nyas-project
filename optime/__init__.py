"""
Initialize the Application.
"""
from flask import Flask

app = Flask(__name__) # pylint: disable=C0103

# weather = climacell.Weather()
#
# @app.route('/')
# def home():
#   return app.send_static_file('index.html'),200
#
# @app.route('/realtime')
# def forecast():
#     "Get real time updates"
#     return str(weather.get_realtime(10, 10, 'si', ['temp', 'temp:F']))
#
# @app.route('/nowcast')
# def nowcast():
#     "Get updates for a 6 hour range"
#     return str(weather.get_nowcast(10, 10, 5, 'si', ['temp', 'temp:F'], "now",
#                "2020-04-13T21:30:50Z"))
#
# @app.route('/hourly')
# def hourly():
#     "Get hourly updates"
#     return str(weather.get_hourly(10, 10, 'si', ['temp', 'temp:F'], "now",
#                "2020-04-14T21:30:50Z"))
#
# @app.route('/daily')
# def daily():
#     "Get daily updates"
#     return str(weather.get_daily(10, 10, 'si', ['temp', 'temp:F'], "now",
#                "2020-04-14T21:30:50Z"))
#
# if __name__ == '__main__':
#   app.run(host="0.0.0.0",port=8000,debug=True)
