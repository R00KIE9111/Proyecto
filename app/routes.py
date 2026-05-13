######################################################
# Importaciones necesarias
######################################################
from app import app
from flask import request, jsonify, render_template, session, redirect, url_for
import uuid
from database.db import *
from gestion.gestion import *
from models.models import *

######################################################
# Rutas API - Clientes
######################################################
@app.route('/clientes', methods=['POST'])
def crearCliente():
    data = request.json
    userId = str(uuid.uuid4())
    cursor = conexion.cursor()
    sql = "INSERT INTO Cliente(userId,nombre,email,passwordHash,rol) VALUES(%s,%s,%s,%s,%s)"
    cursor.execute(sql, (userId, data['nombre'], data['email'], data['passwordHash'], data['rol']))
    conexion.commit()
    cursor.close()

    registrar_evento(userId, 'registro_cliente', request.remote_addr)
    return jsonify({'mensaje': 'Cliente creado', 'userId': userId})

@app.route('/clientes', methods=['GET'])
def obtenerClientes():
    cursor = conexion.cursor()
    cursor.execute("SELECT userId, nombre, email, rol FROM Cliente")
    rows = cursor.fetchall()
    cursor.close()
    clientes = [Cliente(*row) for row in rows]
    return jsonify([c.__dict__ for c in clientes])

######################################################
# Rutas API - Productos
######################################################
@app.route('/productos', methods=['GET'])
def obtenerProductos():
    cursor = conexion.cursor()
    cursor.execute("SELECT productoId, nombre, descripcion, stock, precio, categoria, imagenUrl FROM Producto")
    rows = cursor.fetchall()
    cursor.close()
    productos = [Producto(*row) for row in rows]
    return render_template("index.html", productos=productos)

@app.route('/producto/<productoId>')
def detalleProducto(productoId):
    cursor = conexion.cursor()
    cursor.execute("SELECT productoId, nombre, descripcion, stock, precio, categoria, imagenUrl FROM Producto WHERE productoId=%s", (productoId,))
    row = cursor.fetchone()
    cursor.close()
    producto = Producto(*row) if row else None
    return render_template("detalle_producto.html", producto=producto)

######################################################
# Rutas API - Pedidos
######################################################
@app.route('/mis_pedidos')
def misPedidos():
    clienteId = session.get('userId')
    cursor = conexion.cursor()
    cursor.execute("SELECT pedidoId, clienteId, fecha, total, estado FROM Pedido WHERE clienteId=%s", (clienteId,))
    rows = cursor.fetchall()
    cursor.close()
    pedidos = [Pedido(*row) for row in rows]
    return render_template("pedido.html", pedidos=pedidos)

######################################################
# Rutas API - Carrito
######################################################
@app.route('/carrito')
def carrito():
    return render_template('carrito.html')

@app.route('/carrito_detalle', methods=['POST'])
def agregarProductoCarrito():
    data = request.json
    detalleId = str(uuid.uuid4())
    cursor = conexion.cursor()
    sql = """INSERT INTO CarritoDetalle(detalleId, carritoId, productoId, cantidad)
             VALUES(%s, %s, %s, %s)"""
    cursor.execute(sql, (detalleId, data['carritoId'], data['productoId'], data['cantidad']))
    conexion.commit()
    cursor.close()
    return jsonify({'mensaje': 'Producto agregado al carrito', 'detalleId': detalleId})

######################################################
# Rutas HTML - Login, Perfil, Admin, Logs
######################################################
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    data = request.form
    cursor = conexion.cursor()
    cursor.execute("SELECT userId, rol FROM Cliente WHERE email=%s AND passwordHash=%s",
                   (data['email'], data['password']))
    cliente = cursor.fetchone()
    cursor.close()
    if cliente:
        session['userId'] = cliente[0]
        session['rol'] = cliente[1]
        return redirect(url_for('index'))
    return render_template('login.html', error="Credenciales inválidas")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/perfil', methods=['GET','POST'])
def perfil():
    clienteId = session.get('userId')
    cursor = conexion.cursor()
    if request.method == 'POST':
        data = request.form
        sql = "UPDATE Cliente SET nombre=%s, email=%s WHERE userId=%s"
        cursor.execute(sql, (data['nombre'], data['email'], clienteId))
        conexion.commit()
        cursor.close()
        return redirect(url_for('perfil'))
    cursor.execute("SELECT userId, nombre, email, rol FROM Cliente WHERE userId=%s", (clienteId,))
    row = cursor.fetchone()
    cursor.close()
    cliente = Cliente(*row) if row else None
    return render_template('perfil.html', cliente=cliente)

@app.route('/admin')
def crudAdmin():
    if session.get('rol') != 'admin':
        return redirect(url_for('index'))
    return render_template('crud_admin.html')

@app.route('/logs')
def verLogs():
    eventos = obtener_eventos()
    return render_template('logs.html', eventos=eventos)


######################################################
# Página principal
######################################################
@app.route('/')
def index():
    return obtenerProductos()