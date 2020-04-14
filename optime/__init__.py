"""
Initialize the Application.
"""
import os
import flask

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

    from optime import climacell
    app.register_blueprint(climacell.bp)

    return app
