from sqlalchemy import Column, Integer, String
from DAL.database import Base

class Usuario(Base):
    __tablename__ = 'usuarios'
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    id_rol = Column(Integer, nullable=True)
    contrasena = Column(String(255), nullable=False)