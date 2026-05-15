from flask import render_template, request, redirect, url_for, session
from database.db import *
from functools import wraps
from gestion.gestion import *

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
        if "usuario" not in session:
            return redirect(url_for("login"))
        registrar_evento(session.get("userId"), "ver_index", request.remote_addr)
        return render_template("index.html")
    
    @app.route("/crud_admin")
    @admin_required
    def crud_admin():
        registrar_evento(session.get("userId"), "acceso_crud_admin", request.remote_addr)
        return render_template("crud_admin.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            correo = request.form["correo"]
            password = request.form["password"]
            user = validar_login(correo, password)
            if user:
                session["userId"] = user["userId"]
                session["usuario"] = user["nombre"]
                session["rol"] = user["rol"]
                registrar_evento(user["userId"], "login", request.remote_addr)
                return redirect(url_for("perfil"))

            else:
                return render_template("error.html", mensaje="Credenciales inválidas")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        if "usuario" in session:
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
        productos = listar_productos()
        return render_template("productos.html", productos=productos)

    @app.route("/crear_usuario", methods=["GET", "POST"])
    def crear_usuario_route():
        if request.method == "POST":
            nombre = request.form["nombre"]
            correo = request.form["correo"]
            password = request.form["password"]

            userId = crear_usuario(nombre, correo, password)  # ahora devuelve el ID
            registrar_evento(userId, "crear_usuario", request.remote_addr)

            return redirect(url_for("login"))
        return render_template("crear_usuario.html")

    @app.route("/perfil")
    def perfil():
        nombre = session.get("usuario")
        rol = session.get("rol")
        return render_template("perfil.html", nombre=nombre, rol=rol)
    
    @app.route("/detalle_producto/<int:producto_id>")
    def detalle_producto(producto_id):
        producto = obtener_producto(producto_id)
        return render_template("detalle_producto.html", producto=producto)

    @app.route("/carrito")
    def carrito():
        userId = session.get("userId")
        items = listar_carrito(userId)
        return render_template("carrito.html", items=items)

    @app.route("/carrito/agregar/<int:producto_id>", methods=["POST"])
    def agregar_carrito(producto_id):
        cantidad = int(request.form["cantidad"])
        userId = session.get("userId")   # ojo: aquí conviene usar el ID, no el nombre
        agregar_al_carrito(userId, producto_id, cantidad)
        registrar_evento(userId, f"agregar_carrito_producto_{producto_id}", request.remote_addr)
        return redirect(url_for("carrito"))

    @app.route("/pedido/crear")
    def pedido_crear():
        userId = session.get("userId")
        pedidoId = crear_pedido(userId)
        registrar_evento(userId, f"crear_pedido_{pedidoId}", request.remote_addr)
        return render_template("pedido_confirmacion.html", pedidoId=pedidoId)