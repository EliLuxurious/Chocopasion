from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from .service_usuario import UsuarioService

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if UsuarioService.verificar_credenciales(username, password):
            session['usuario'] = username
            return redirect(url_for('produccion.index'))
        else:
            flash("Credenciales incorrectas", "error")
    return render_template("usuario/login.html")

@usuario_bp.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('usuario_bp.login'))

@usuario_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        datos = {
            'username': request.form['username'],
            'password': request.form['password']
        }
        resultado = UsuarioService.registrar(datos)
        if resultado.get("error"):
            flash(resultado["error"], "error")
        else:
            flash("Usuario registrado exitosamente", "success")
            return redirect(url_for('usuario_bp.login'))
    return render_template("usuario/registro.html")
