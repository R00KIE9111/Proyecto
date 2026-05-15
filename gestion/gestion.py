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
def agregar_al_carrito(clienteId, productoId, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT carritoId FROM Carrito WHERE clienteId=%s", (clienteId,))
    carrito = cursor.fetchone()
    if carrito:
        carritoId = carrito[0]
    else:
        carritoId = f"CARR{clienteId}"
        cursor.execute(
            "INSERT INTO Carrito (carritoId, clienteId, fechaCreacion, total) VALUES (%s, %s, NOW(), 0)",
            (carritoId, clienteId)
        )
    cursor.execute(
        "SELECT cantidad FROM CarritoDetalle WHERE carritoId=%s AND productoId=%s",
        (carritoId, productoId)
    )
    existente = cursor.fetchone()
    if existente:
        nueva_cantidad = existente[0] + cantidad
        cursor.execute(
            "UPDATE CarritoDetalle SET cantidad=%s WHERE carritoId=%s AND productoId=%s",
            (nueva_cantidad, carritoId, productoId)
        )
    else:
        carDetId = f"{carritoId}_{productoId}"
        cursor.execute(
            "INSERT INTO CarritoDetalle (carDetId, carritoId, productoId, cantidad) VALUES (%s, %s, %s, %s)",
            (carDetId, carritoId, productoId, cantidad)
        )
    cursor.execute("SELECT precio FROM Producto WHERE productoId=%s", (productoId,))
    precio = cursor.fetchone()[0]
    subtotal = cantidad * precio
    cursor.execute("UPDATE Carrito SET total = total + %s WHERE carritoId=%s", (subtotal, carritoId))
    conn.commit()
    cursor.close()
    conn.close()

def eliminar_del_carrito(clienteId, productoId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT carritoId FROM Carrito WHERE clienteId=%s", (clienteId,))
    carrito = cursor.fetchone()
    if not carrito:
        conn.close()
        return
    carritoId = carrito[0]
    cursor.execute(
        "SELECT cd.cantidad, p.precio FROM CarritoDetalle cd JOIN Producto p ON cd.productoId=p.productoId WHERE cd.carritoId=%s AND cd.productoId=%s",
        (carritoId, productoId)
    )
    item = cursor.fetchone()
    if item:
        cantidad, precio = item
        subtotal = cantidad * precio
        cursor.execute(
            "DELETE FROM CarritoDetalle WHERE carritoId=%s AND productoId=%s",
            (carritoId, productoId)
        )
        cursor.execute(
            "UPDATE Carrito SET total = total - %s WHERE carritoId=%s",
            (subtotal, carritoId)
        )
    conn.commit()
    cursor.close()
    conn.close()

def listar_carrito(clienteId):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = """
        SELECT cd.productoId, p.nombre, p.precio, cd.cantidad,
               (p.precio * cd.cantidad) AS subtotal
        FROM CarritoDetalle cd
        JOIN Carrito c ON cd.carritoId = c.carritoId
        JOIN Producto p ON cd.productoId = p.productoId
        WHERE c.clienteId = %s
    """
    cursor.execute(query, (clienteId,))
    items = cursor.fetchall()
    cursor.execute("SELECT total FROM Carrito WHERE clienteId=%s", (clienteId,))
    total = cursor.fetchone()["total"]
    conn.close()
    return items, total

def finalizar_compra(clienteId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT carritoId, total FROM Carrito WHERE clienteId=%s", (clienteId,))
    carrito = cursor.fetchone()
    if not carrito:
        conn.close()
        return None
    carritoId, total = carrito
    pedidoId = f"PED{carritoId}"
    cursor.execute(
        "INSERT INTO Pedido (pedidoId, clienteId, fechaPedido, total) VALUES (%s, %s, NOW(), %s)",
        (pedidoId, clienteId, total)
    )
    cursor.execute(
        "SELECT productoId, cantidad FROM CarritoDetalle WHERE carritoId=%s",
        (carritoId,)
    )
    productos = cursor.fetchall()
    for productoId, cantidad in productos:
        cursor.execute(
            "INSERT INTO PedidoDetalle (pedidoId, productoId, cantidad) VALUES (%s, %s, %s)",
            (pedidoId, productoId, cantidad)
        )
    cursor.execute("DELETE FROM CarritoDetalle WHERE carritoId=%s", (carritoId,))
    cursor.execute("UPDATE Carrito SET total=0 WHERE carritoId=%s", (carritoId,))
    conn.commit()
    cursor.close()
    conn.close()
    return pedidoId


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