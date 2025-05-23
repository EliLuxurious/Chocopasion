from DAL.database import session
from .model import Produccion

class ProduccionRepository:
    def obtener_todos(self):
        return session.query(Produccion).all()

    def agregar(self, produccion):
        session.add(produccion)
        session.commit()

    def obtener_por_id(self, id_produccion):
        return session.query(Produccion).filter_by(id_produccion=id_produccion).first()

    def eliminar(self, id_produccion):
        produccion = self.obtener_por_id(id_produccion)
        if produccion:
            session.delete(produccion)
            session.commit()