from flask import Flask
from . import routes

def create_app():
    app = routes.app
    return app