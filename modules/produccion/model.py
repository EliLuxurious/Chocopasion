from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from DAL.database import Base

class Produccion(Base):
    __tablename__ = 'produccion'
    id_produccion = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    id_presentacion = Column(Integer, ForeignKey('presentaciones.id_presentacion'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=False)

    producto = relationship("Producto")
    presentacion = relationship("Presentacion")