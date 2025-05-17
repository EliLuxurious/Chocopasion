from .service import ProductoService

class ProductoController:
    def __init__(self):
        self.producto_service = ProductoService()

    def listar_productos(self):
        productos = self.producto_service.obtener_productos()
        return [{"id": producto.id_producto, "nombre": producto.nombre} for producto in productos]

    def agregar_producto(self, nombre):
        self.producto_service.agregar_producto(nombre)
        return {"mensaje": "Producto agregado exitosamente"}

    def eliminar_producto(self, id_producto):
        self.producto_service.eliminar_producto(id_producto)
        return {"mensaje": "Producto eliminado exitosamente"}