from .repository import PrecioRepository
from .model import Precio

class PrecioService:
    def __init__(self):
        self.precio_repository = PrecioRepository()

    def obtener_precios(self):
        return self.precio_repository.obtener_todos()

    def obtener_precio_por_id(self, id_precio):
        return self.precio_repository.obtener_por_id(id_precio)

    def crear_precio(self, id_producto, id_presentacion, precio_unitario):
        """Crear un nuevo precio"""
        nuevo_precio = Precio(
            id_producto=id_producto,
            id_presentacion=id_presentacion,
            precio_unitario=precio_unitario
        )
        
        return self.precio_repository.agregar(nuevo_precio)

    def actualizar_precio(self, id_precio, id_producto, id_presentacion, precio_unitario):
        """Actualizar un precio existente"""
        precio = Precio(
            id_precio=id_precio,
            id_producto=id_producto,
            id_presentacion=id_presentacion,
            precio_unitario=precio_unitario
        )
        
        return self.precio_repository.actualizar(precio)

    def eliminar_precio(self, id_precio):
        return self.precio_repository.eliminar(id_precio)

    def obtener_productos(self):
        return self.precio_repository.obtener_productos()

    def obtener_presentaciones(self):
        return self.precio_repository.obtener_presentaciones()

    def obtener_precio_actual(self, id_producto, id_presentacion):
        """Obtener el precio actual para un producto y presentación"""
        return self.precio_repository.obtener_precio_actual(id_producto, id_presentacion)

    def obtener_presentaciones_con_precio(self, id_producto):
        """Obtener presentaciones que tienen precio configurado para un producto específico"""
        return self.precio_repository.obtener_presentaciones_con_precio(id_producto)
