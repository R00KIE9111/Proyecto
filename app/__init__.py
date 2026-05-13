# proyecto/app/__init__.py
from flask import Flask

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# Importa las rutas después de crear la instancia
from app import routes