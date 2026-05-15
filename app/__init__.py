from flask import Flask
from .routes import init_routes

def create_app():
    app = Flask(__name__)
    app.secret_key = "clave-secreta"  # cámbiala en producción

    # Registrar rutas
    init_routes(app)

    return app