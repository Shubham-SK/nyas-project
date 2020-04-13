"""
Initialize the Application.
"""
from flask import Flask

# initialize app
app = Flask(__name__) # pylint: disable=C0103

# load third party secret keys
app.config.from_object('config')
app.config.from_pyfile('config.py')
