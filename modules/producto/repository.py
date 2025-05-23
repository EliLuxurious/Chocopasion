from DAL.database import session
from .model import Producto

class ProductoRepository:
    def obtener_todos(self):
        return session.query(Producto).all()

    def agregar(self, producto):
        session.add(producto)
        session.commit()

    def obtener_por_id(self, id_producto):
        return session.query(Producto).filter_by(id_producto=id_producto).first()

    def eliminar(self, id_producto):
        producto = self.obtener_por_id(id_producto)
        if producto:
            session.delete(producto)
            session.commit()