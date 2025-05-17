from sqlalchemy import Column, Integer, String, Float
from infrastructure.database import db

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    precio = Column(Float, nullable=False)
    unidad = Column(String(20), nullable=False)
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'unidad': self.unidad
        }
