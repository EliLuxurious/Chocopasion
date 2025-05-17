from DAL.database import session
from .model import Usuario

class UsuarioRepository:
    def obtener_todos(self):
        return session.query(Usuario).all()

    def agregar(self, usuario):
        session.add(usuario)
        session.commit()

    def obtener_por_id(self, id_usuario):
        return session.query(Usuario).filter_by(id_usuario=id_usuario).first()

    def eliminar(self, id_usuario):
        usuario = self.obtener_por_id(id_usuario)
        if usuario:
            session.delete(usuario)
            session.commit()