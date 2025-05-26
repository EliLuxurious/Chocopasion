from .service import UsuarioService
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

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

usuario_bp = Blueprint('usuario', __name__)
usuario_service = UsuarioService()

@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usuario = usuario_service.verificar_login(email, password)
        
        if usuario:
            session.clear()  # Seguridad: limpiar sesión previa
            session['usuario_id'] = usuario.id_usuario
            session['rol'] = usuario.rol.lower()

            if session['rol'] == 'administrador':
                return redirect(url_for('dashboard'))  # admin → dashboard
            elif session['rol'] == 'empleado':
                return render_template('home.html')  # empleado → página personalizada
            else:
                flash('Rol desconocido', 'danger')
                return redirect(url_for('login'))
        else:
            return render_template('usuario/login.html', error='Credenciales inválidas')

    return render_template('usuario/login.html')
