from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey
from infrastructure.database import Base

class Produccion(Base):
    __tablename__ = 'produccion'
    id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    producto_id = Column(Integer, ForeignKey('productos.id'))
    cantidad = Column(DECIMAL)
    unidad = Column(String(50))
    responsable_id = Column(Integer, ForeignKey('usuarios.id'))
