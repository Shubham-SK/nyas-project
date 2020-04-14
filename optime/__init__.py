"""
Initialize the Application.
"""
import os
import flask

def create_app(test_config=None):
    "Create and configure app"
    app = flask.Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load secret keys
        app.config.from_object("config")
        app.config.from_pyfile("config.py")
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
