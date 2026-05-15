import hashlib
from database.db import get_connection
import uuid

def generar_user_id():
    return "USR" + str(uuid.uuid4())[:8]

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def crear_usuario(nombre, correo, password, rol="cliente"):
    userId = generar_user_id()
    hashed_password = hash_password(password)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Cliente (userId, nombre, correo, password, rol) VALUES (%s, %s, %s, %s, %s)",
        (userId, nombre, correo, hashed_password, rol)
    )
    conn.commit()
    cursor.close()
    conn.close()

def listar_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT productoId, nombre, precio FROM Producto")
    productos = cursor.fetchall()
    conn.close()
    return productos

def validar_login(correo, password):
    hashed_password = hash_password(password)
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Cliente WHERE correo=%s AND password=%s", (correo, hashed_password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def obtener_producto(producto_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Producto WHERE productoId=%s", (producto_id,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()
    return producto

def agregar_al_carrito(userId, productoId, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Carrito (userId, productoId, cantidad) VALUES (%s, %s, %s)",
        (userId, productoId, cantidad)
    )
    conn.commit()
    cursor.close()
    conn.close()

def crear_pedido(userId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Pedido (userId, estado) VALUES (%s, %s)",
        (userId, "pendiente")
    )
    conn.commit()
    cursor.close()
    conn.close()

def obtener_producto(producto_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Producto WHERE productoId=%s", (producto_id,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()
    return producto

def agregar_al_carrito(userId, productoId, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Carrito (userId, productoId, cantidad) VALUES (%s, %s, %s)",
        (userId, productoId, cantidad)
    )
    conn.commit()
    cursor.close()
    conn.close()

def listar_carrito(userId):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.carritoId, p.nombre, p.precio, c.cantidad
        FROM Carrito c
        JOIN Producto p ON c.productoId = p.productoId
        WHERE c.userId=%s
    """, (userId,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items

def crear_pedido(userId):
    conn = get_connection()
    cursor = conn.cursor()
    # Crear pedido
    cursor.execute("INSERT INTO Pedido (userId, estado) VALUES (%s, %s)", (userId, "pendiente"))
    pedidoId = cursor.lastrowid
    # Pasar items del carrito al detalle del pedido
    cursor.execute("SELECT productoId, cantidad FROM Carrito WHERE userId=%s", (userId,))
    items = cursor.fetchall()
    for item in items:
        cursor.execute(
            "INSERT INTO DetallePedido (pedidoId, productoId, cantidad) VALUES (%s, %s, %s)",
            (pedidoId, item[0], item[1])
        )
    cursor.execute("DELETE FROM Carrito WHERE userId=%s", (userId,))
    conn.commit()
    cursor.close()
    conn.close()
    return pedidoId