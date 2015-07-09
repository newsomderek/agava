""" Agava Server
"""

from flask import Flask, Request, Response
from agava.app import init_app

#from flask_sslify import SSLify

application = app = init_app()

if __name__ == '__main__':
    app.run()
