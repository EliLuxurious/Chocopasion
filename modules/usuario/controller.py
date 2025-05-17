from .service import UsuarioService

class UsuarioController:
    def __init__(self):
        self.usuario_service = UsuarioService()

    def listar_usuarios(self):
        usuarios = self.usuario_service.obtener_usuarios()
        return [{"id": usuario.id_usuario, "nombre": usuario.nombre, "email": usuario.email} for usuario in usuarios]

    def agregar_usuario(self, nombre, email):
        self.usuario_service.agregar_usuario(nombre, email)
        return {"mensaje": "Usuario agregado exitosamente"}

    def eliminar_usuario(self, id_usuario):
        self.usuario_service.eliminar_usuario(id_usuario)
        return {"mensaje": "Usuario eliminado exitosamente"}