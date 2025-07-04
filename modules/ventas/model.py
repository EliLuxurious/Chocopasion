from datetime import datetime

class Venta:
    def __init__(self, id_venta=None, fecha=None, id_producto=None, id_presentacion=None,
                 cantidad=None, precio_unitario=None, total=None, 
                 producto_nombre=None, presentacion_nombre=None):
        self.id_venta = id_venta
        self.fecha = fecha or datetime.now().date()
        self.id_producto = id_producto
        self.id_presentacion = id_presentacion
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.total = total
        self.producto_nombre = producto_nombre
        self.presentacion_nombre = presentacion_nombre
