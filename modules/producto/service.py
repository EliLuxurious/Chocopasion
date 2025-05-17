from .repository import ProductoRepository
from .model import Producto

class ProductoService:
    def __init__(self):
        self.producto_repository = ProductoRepository()

    def obtener_productos(self):
        return self.producto_repository.obtener_todos()

    def agregar_producto(self, nombre):
        nuevo_producto = Producto(nombre=nombre)
        self.producto_repository.agregar(nuevo_producto)

    def eliminar_producto(self, id_producto):
        self.producto_repository.eliminar(id_producto)