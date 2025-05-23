from sqlalchemy import Column, Integer, String
from DAL.database import Base

class Producto(Base):
    __tablename__ = 'productos'
    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)