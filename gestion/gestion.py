import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime

# --- Conexión a la BD ---
def get_connection():
    return pymysql.connect(
        host="database-1.c7saowikmas3.us-east-1.rds.amazonaws.com",
        user="admin",
        password="Inacap.2026",
        database="gestorecommerce"
    )

# --- Autenticación ---
def validar_login(email, password):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Cliente WHERE email=%s", (email,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user["passwordHash"], password):
        return user
    return None

def crear_usuario(nombre, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    userId = str(uuid.uuid4())
    hashed = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO Cliente (userId, nombre, email, passwordHash, rol) VALUES (%s,%s,%s,%s,%s)",
        (userId, nombre, email, hashed, "cliente")
    )
    conn.commit()
    conn.close()

def obtener_usuario(userId):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "SELECT userId, nombre, email, rol FROM Cliente WHERE userId=%s",
        (userId,)
    )
    usuario = cursor.fetchone()
    conn.close()
    return usuario

# --- Productos ---
def listar_productos():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Producto")
    productos = cursor.fetchall()
    conn.close()
    return productos

def obtener_producto(productoId):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Producto WHERE productoId=%s", (productoId,))
    producto = cursor.fetchone()
    conn.close()
    return producto

def nuevo_producto(datos):
    conn = get_connection()
    cursor = conn.cursor()
    productoId = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO Producto (productoId, nombre, descripcion, precio, stock) VALUES (%s,%s,%s,%s,%s)",
        (productoId, datos["nombre"], datos["descripcion"], datos["precio"], datos["stock"])
    )
    conn.commit()
    conn.close()

def editar_producto(productoId, datos):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Producto SET nombre=%s, descripcion=%s, precio=%s, stock=%s WHERE productoId=%s",
        (datos["nombre"], datos["descripcion"], datos["precio"], datos["stock"], productoId)
    )
    conn.commit()
    conn.close()

def eliminar_producto(productoId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Producto WHERE productoId=%s", (productoId,))
    conn.commit()
    conn.close()

# --- Carrito ---
def agregar_al_carrito(userId, productoId, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Carrito (userId, productoId, cantidad) VALUES (%s,%s,%s)",
        (userId, productoId, cantidad)
    )
    conn.commit()
    conn.close()

def listar_carrito(userId):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT c.productoId, p.nombre, p.precio, c.cantidad
        FROM Carrito c
        JOIN Producto p ON c.productoId = p.productoId
        WHERE c.userId=%s
    """, (userId,))
    items = cursor.fetchall()
    conn.close()
    return items

def eliminar_del_carrito(userId, productoId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Carrito WHERE userId=%s AND productoId=%s", (userId, productoId))
    conn.commit()
    conn.close()

# --- Pedidos ---
def crear_pedido(userId):
    conn = get_connection()
    cursor = conn.cursor()
    pedidoId = str(uuid.uuid4())
    fecha = datetime.now()
    cursor.execute("INSERT INTO Pedido (pedidoId, userId, fecha) VALUES (%s,%s,%s)", (pedidoId, userId, fecha))
    conn.commit()
    conn.close()
    return pedidoId

def listar_pedidos(userId):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Pedido WHERE userId=%s", (userId,))
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

# --- Logs ---
def registrar_evento(userId, accion):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Logs (userId, accion, timestamp) VALUES (%s, %s, %s)",
        (userId, accion, fecha)
    )
    conn.commit()
    cursor.close()
    conn.close()


def listar_logs():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return logs