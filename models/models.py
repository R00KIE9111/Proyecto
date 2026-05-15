class Cliente:
    def __init__(self, clienteId, nombre, correo, telefono, rol="cliente"):
        self.clienteId = clienteId
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.rol = rol

    def __repr__(self):
        return f"<Cliente {self.nombre} ({self.correo})>"


class Producto:
    def __init__(self, productoId, nombre, descripcion, precio, stock):
        self.productoId = productoId
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock

    def __repr__(self):
        return f"<Producto {self.nombre} - ${self.precio}>"


class Carrito:
    def __init__(self, carritoId, clienteId):
        self.carritoId = carritoId
        self.clienteId = clienteId
        self.items = []  # lista de CarritoDetalle

    def agregar_item(self, item):
        self.items.append(item)

    def calcular_total(self):
        return sum([i.cantidad * i.producto.precio for i in self.items])


class CarritoDetalle:
    def __init__(self, producto, cantidad):
        self.producto = producto
        self.cantidad = cantidad


class Pedido:
    def __init__(self, pedidoId, clienteId, fecha, total, estado="pendiente"):
        self.pedidoId = pedidoId
        self.clienteId = clienteId
        self.fecha = fecha
        self.total = total
        self.estado = estado

    def __repr__(self):
        return f"<Pedido {self.pedidoId} - Total: ${self.total}>"