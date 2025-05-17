from .repository import ProduccionRepository
from .model import Produccion

class ProduccionService:
    def __init__(self):
        self.produccion_repository = ProduccionRepository()

    def obtener_producciones(self):
        return self.produccion_repository.obtener_todos()

    def agregar_produccion(self, id_producto, id_presentacion, cantidad, fecha):
        nueva_produccion = Produccion(
            id_producto=id_producto,
            id_presentacion=id_presentacion,
            cantidad=cantidad,
            fecha=fecha
        )
        self.produccion_repository.agregar(nueva_produccion)

    def eliminar_produccion(self, id_produccion):
        self.produccion_repository.eliminar(id_produccion)