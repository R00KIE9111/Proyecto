from flask import render_template, request, redirect, url_for, session
from database.db import get_connection, registrar_evento
from functools import wraps

# Decorador para rutas admin
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("rol") != "admin":
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper

def init_routes(app):

    @app.route("/")
    def index():
        if "userId" not in session:
            return redirect(url_for("login"))
        registrar_evento(session["userId"], "ver_index", request.remote_addr)
        return render_template("index.html")
    
    @app.route("/crud_admin")
    @admin_required
    def crud_admin():
        registrar_evento(session["userId"], "acceso_crud_admin", request.remote_addr)
        return render_template("crud_admin.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            user = None
            conn = None
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT userId, rol FROM Cliente WHERE email=%s AND passwordHash=%s", (email, password))
                user = cursor.fetchone()
            except Exception as e:
                print("Error:", e)
            finally:
                if conn:
                    conn.close()

            if user:
                session["userId"] = user[0]
                session["rol"] = user[1]
                registrar_evento(user[0], "login", request.remote_addr)
                return redirect(url_for("index"))
            else:
                return render_template("error.html", mensaje="Credenciales inválidas")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        if "userId" in session:
            registrar_evento(session["userId"], "logout", request.remote_addr)
        session.clear()
        return redirect(url_for("login"))
    
    @app.route("/logs")
    @admin_required
    def logs():
        registrar_evento(session["userId"], "acceso_logs", request.remote_addr)
        return render_template("logs.html")
    
    @app.route("/productos")
    def productos():
        return render_template("productos.html")
    
    @app.route("/carrito")
    def carrito():
        return render_template("carrito.html")

    @app.route("/crear_usuario", methods=["GET", "POST"])
    def crear_usuario():
        if request.method == "POST":
            # lógica para insertar usuario en RDS
            return redirect(url_for("login"))
        return render_template("crear_usuario.html")

    @app.route("/detalle_producto/<int:producto_id>")
    def detalle_producto(producto_id):
        # Aquí podrías cargar detalle desde RDS
        return render_template("detalle_producto.html", producto_id=producto_id)