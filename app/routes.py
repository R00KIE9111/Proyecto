from flask import Flask, render_template, request, redirect, url_for, session, flash
from gestion.gestion import *

app = Flask(__name__)
app.secret_key = "clave_secreta"

# --- Autenticación ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]
        user = validar_login(correo, password)
        if user:
            session["usuario"] = user["nombre"]
            session["rol"] = user["rol"]
            session["userId"] = user["userId"]
            registrar_evento(user["userId"], "Login exitoso")
            return redirect(url_for("perfil"))
        else:
            return render_template("error.html", mensaje="Credenciales inválidas")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# --- Usuarios ---
@app.route("/crear_usuario", methods=["GET", "POST"])
def crear_usuario_route():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]
        crear_usuario(nombre, correo, password)
        flash("Usuario creado correctamente", "success")
        return redirect(url_for("login"))
    return render_template("crear_usuario.html")

@app.route("/crud_admin")
def crud_admin():
    if session.get("rol") != "admin":
        flash("Acceso denegado", "danger")
        return redirect(url_for("productos"))

    productos = listar_productos()
    return render_template("crud_admin.html", productos=productos)

@app.route("/perfil")
def perfil():
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario = obtener_usuario(session["userId"])
    return render_template("perfil.html", usuario=usuario)

# --- Productos ---
@app.route("/productos")
def productos():
    lista = listar_productos()
    return render_template("index.html", productos=lista)

@app.route("/detalle_producto/<producto_id>")
def detalle_producto(producto_id):
    producto = obtener_producto(producto_id)
    return render_template("detalle_producto.html", producto=producto)

@app.route("/producto/nuevo", methods=["GET", "POST"])
def nuevo_producto_route():
    if session.get("rol") != "admin":
        return render_template("error.html", mensaje="Acceso denegado")
    if request.method == "POST":
        nuevo_producto(request.form)
        return redirect(url_for("productos"))
    return render_template("producto.html")

@app.route("/producto/editar/<int:producto_id>", methods=["GET", "POST"])
def editar_producto_route(producto_id):
    if session.get("rol") != "admin":
        flash("Acceso denegado", "danger")
        return redirect(url_for("productos"))
    producto = obtener_producto(producto_id)
    if request.method == "POST":
        datos = {
            "nombre": request.form["nombre"],
            "descripcion": request.form["descripcion"],
            "precio": request.form["precio"],
            "stock": request.form["stock"]
        }
        editar_producto(producto_id, datos)
        flash("Producto actualizado correctamente", "success")
        return redirect(url_for("productos"))
    return render_template("editar_producto.html", producto=producto)


@app.route("/producto/eliminar/<int:producto_id>")
def eliminar_producto_route(producto_id):
    eliminar_producto(producto_id)
    return redirect(url_for("productos"))

# --- Carrito ---
@app.route("/carrito")
def carrito():
    clienteId = session.get("userId")
    items, total = listar_carrito(clienteId)
    return render_template("carrito.html", items=items, total=total)

@app.route("/carrito/agregar/<producto_id>", methods=["POST"])
def agregar_carrito(producto_id):
    cantidad = int(request.form["cantidad"])
    agregar_al_carrito(session.get("userId"), producto_id, cantidad)
    return redirect(url_for("carrito"))

@app.route("/carrito/eliminar/<productoId>", methods=["POST"])
def eliminar_carrito(productoId):
    clienteId = session.get("userId")
    eliminar_del_carrito(clienteId, productoId)
    return redirect(url_for("carrito"))

@app.route("/carrito/comprar", methods=["POST"])
def comprar():
    clienteId = session.get("userId")
    pedidoId = finalizar_compra(clienteId)
    if pedidoId:
        flash("Compra realizada con éxito", "success")
        return redirect(url_for("pedido", pedidoId=pedidoId))
    else:
        flash("No se pudo finalizar la compra. Carrito vacío.", "danger")
        return redirect(url_for("carrito"))

# --- Pedidos ---
@app.route("/pedido/crear")
def pedido_crear():
    pedidoId = crear_pedido(session.get("userId"))
    return render_template("pedido.html", pedidoId=pedidoId)

@app.route("/pedido")
def pedidos():
    lista = listar_pedidos(session.get("userId"))
    return render_template("pedido.html", pedidos=lista)

@app.route("/pedido/<pedidoId>")
def pedido(pedidoId):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Pedido WHERE pedidoId=%s", (pedidoId,))
    pedido = cursor.fetchone()
    cursor.execute(
        """SELECT pd.productoId, p.nombre, pd.cantidad, p.precio,
                  (pd.cantidad * p.precio) AS subtotal
           FROM PedidoDetalle pd
           JOIN Producto p ON pd.productoId = p.productoId
           WHERE pd.pedidoId=%s""",
        (pedidoId,)
    )
    detalles = cursor.fetchall()
    conn.close()
    return render_template("pedido.html", pedido=pedido, detalles=detalles)

# --- Logs ---
@app.route("/logs")
def logs():
    if session.get("rol") != "admin":
        return render_template("error.html", mensaje="Acceso denegado")
    lista = listar_logs()
    return render_template("logs.html", logs=lista)

# --- Inicio ---
@app.route("/")
def index():
    lista = listar_productos()
    return render_template("index.html", productos=lista)