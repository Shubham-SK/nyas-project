"""
Invoke to Start up a Development Server.
"""
from application import app

@app.route('/')
def index():
    """
    Testing with hello world.
    """
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
