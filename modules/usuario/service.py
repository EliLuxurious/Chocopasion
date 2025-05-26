from .repository import UsuarioRepository
from .model import Usuario

class UsuarioService:
    def __init__(self):
        self.usuario_repository = UsuarioRepository()

    def obtener_usuarios(self):
        return self.usuario_repository.obtener_todos()

    def agregar_usuario(self, nombre, email):
        nuevo_usuario = Usuario(nombre=nombre, email=email)
        self.usuario_repository.agregar(nuevo_usuario)

    def eliminar_usuario(self, id_usuario):
        self.usuario_repository.eliminar(id_usuario)

    def verificar_login(self, email, password):
        return self.usuario_repository.verificar_login(email, password)