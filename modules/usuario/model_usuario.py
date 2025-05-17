from sqlalchemy import Column, Integer, String
from infrastructure.database import Base

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    correo = Column(String(100))
    password = Column(String(255))
