from flask import Flask
from flask_wtf.csrf import CSRFProtect
from .routes import init_routes

def create_app():
    app = Flask(__name__)
    app.secret_key = "clave-secreta"  # cámbiala en producción

    # Protección CSRF
    CSRFProtect(app)

    # Registrar rutas
    init_routes(app)

    return app