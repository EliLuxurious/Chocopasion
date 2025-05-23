from .service import ProduccionService

class ProduccionController:
    def __init__(self):
        self.produccion_service = ProduccionService()

    def listar_producciones(self):
        producciones = self.produccion_service.obtener_producciones()
        return [
            {
                "id": produccion.id_produccion,
                "id_producto": produccion.id_producto,
                "id_presentacion": produccion.id_presentacion,
                "cantidad": produccion.cantidad,
                "fecha": produccion.fecha.strftime("%Y-%m-%d")
            }
            for produccion in producciones
        ]

    def agregar_produccion(self, id_producto, id_presentacion, cantidad, fecha):
        self.produccion_service.agregar_produccion(id_producto, id_presentacion, cantidad, fecha)
        return {"mensaje": "Producción agregada exitosamente"}

    def eliminar_produccion(self, id_produccion):
        self.produccion_service.eliminar_produccion(id_produccion)
        return {"mensaje": "Producción eliminada exitosamente"}