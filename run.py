from app import app

import pymysql

def inicializar_db():
    conexion = pymysql.connect(
        host='flask-db.c7saowikmas3.us-east-1.rds.amazonaws.com',
        user='admin',
        password='Inacap.2026',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conexion.cursor()

    # Crear base de datos si no existe
    cursor.execute("CREATE DATABASE IF NOT EXISTS gestorecommerce;")
    cursor.execute("USE gestorecommerce;")

    # Crear tablas mínimas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Cliente (
        clienteId INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        passwordHash VARCHAR(255),
        rol VARCHAR(50)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Producto (
        productoId INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100),
        precio DECIMAL(10,2),
        stock INT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pedido (
        pedidoId INT AUTO_INCREMENT PRIMARY KEY,
        clienteId INT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total DECIMAL(10,2),
        FOREIGN KEY (clienteId) REFERENCES Cliente(clienteId)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Carrito (
        carritoId INT AUTO_INCREMENT PRIMARY KEY,
        clienteId INT,
        FOREIGN KEY (clienteId) REFERENCES Cliente(clienteId)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CarritoDetalle (
        detalleId INT AUTO_INCREMENT PRIMARY KEY,
        carritoId INT,
        productoId INT,
        cantidad INT,
        FOREIGN KEY (carritoId) REFERENCES Carrito(carritoId),
        FOREIGN KEY (productoId) REFERENCES Producto(productoId)
    );
    """)

    conexion.commit()
    conexion.close()

# Llamar antes de iniciar Flask
inicializar_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
