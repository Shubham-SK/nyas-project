"""
Initialize the Application.
"""
import optime_app.loginRoutes
import optime_app.shoppingRoutes
import optime_app.schedulingRoutes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
