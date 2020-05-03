from setuptools import setup

setup(
    name='optime_app',
    packages=['optime_app'],
    include_package_data=True,
    install_requires=[
        'flask',
        'functools',
        'datetime',
        'pytz',
        'bson',
        'pymongo',
        'tzwhere',
        'werkzeug'
    ],
)
