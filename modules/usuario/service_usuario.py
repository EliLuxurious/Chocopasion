from .repository_usuario import UsuarioRepository

class UsuarioService:

    @staticmethod
    def verificar_credenciales(username, password):
        usuario = UsuarioRepository.buscar_por_username(username)
        if usuario and usuario['password'] == password:
            return True
        return False

    @staticmethod
    def registrar(data):
        if not data.get('username') or not data.get('password'):
            return {"error": "Todos los campos son obligatorios"}

        existente = UsuarioRepository.buscar_por_username(data['username'])
        if existente:
            return {"error": "El nombre de usuario ya existe"}

        UsuarioRepository.insertar(data)
        return {"mensaje": "Registrado"}
