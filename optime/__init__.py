"""
Initialize the Application.
"""
import os
import flask
from climacell import Weather

def create_app(test_config=None):
    "Create and configure app"
    app = flask.Flask(__name__, static_url_path='/static', instance_relative_config=True)
    if test_config is None:
        # load secret keys
        #app.config.from_object("config")
        app.config.from_pyfile("config.py")
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app

app = create_app()
weather = Weather()

@app.route('/')
def home():
  return app.send_static_file('index.html'),200

@app.route('/realtime')
def forecast():
  return str(weather.get_realtime(10, 10, 'si', ['temp', 'temp:F']))

@app.route('/nowcast')
def nowcast():
  return str(weather.get_nowcast(10, 10, 5, 'si', ['temp', 'temp:F'], "now",
  "2020-04-13T21:30:50Z"))

@app.route('/hourly')
def hourly():
  return str(weather.get_hourly(10, 10, 'si', ['temp', 'temp:F'], "now",
  "2020-04-14T21:30:50Z"))

@app.route('/daily')
def daily():
  return str(weather.get_daily(10, 10, 'si', ['temp', 'temp:F'], "now",
  "2020-04-14T21:30:50Z"))

if __name__ == '__main__':
  app.run(host="0.0.0.0",port=8000,debug=True)
