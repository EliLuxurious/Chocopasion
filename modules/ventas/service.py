from .repository import VentaRepository
from .model import Venta
from datetime import datetime

class VentaService:
    def __init__(self):
        self.venta_repository = VentaRepository()

    def obtener_ventas(self):
        return self.venta_repository.obtener_todas()

    def obtener_venta_por_id(self, id_venta):
        return self.venta_repository.obtener_por_id(id_venta)

    def crear_venta(self, fecha, id_producto, id_presentacion, cantidad, precio_unitario):
        """Crear una nueva venta"""
        # Convertir fecha si viene como string
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        nueva_venta = Venta(
            fecha=fecha,
            id_producto=id_producto,
            id_presentacion=id_presentacion,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )
        
        return self.venta_repository.agregar(nueva_venta)

    def eliminar_venta(self, id_venta):
        return self.venta_repository.eliminar(id_venta)

    def buscar_ventas_por_fecha(self, fecha_inicio, fecha_fin):
        return self.venta_repository.obtener_ventas_por_fecha(fecha_inicio, fecha_fin)

    def obtener_productos(self):
        return self.venta_repository.obtener_productos()

    def obtener_presentaciones(self):
        return self.venta_repository.obtener_presentaciones()

    def obtener_precio_vigente(self, id_producto, id_presentacion, fecha=None):
        """Obtener el precio vigente para un producto y presentación"""
        return self.venta_repository.obtener_precio_vigente(id_producto, id_presentacion, fecha)
