from database.db import get_connection

def listar_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT productoId, nombre, precio FROM Producto")
    productos = cursor.fetchall()
    conn.close()
    return productos
