# from flask import Flask, session, redirect, url_for
# from infrastructure.config import Config
# from modules.produccion.controller import produccion_bp
# from modules.usuario.controller import usuario_bp

# app = Flask(__name__)
# app.config.from_object(Config)
# app.secret_key = "clave_secreta_segura"  # Requerido para sesiones y flash

# # Registrar Blueprints de usuario y producción
# app.register_blueprint(usuario_bp, url_prefix="/usuarios")
# app.register_blueprint(produccion_bp, url_prefix="/produccion")

# # Ruta principal
# @app.route('/')
# def home():
#     return "<h2>Bienvenido al sistema</h2><p>Visita <a href='/usuarios/login'>/Ingresar</a></p>"

# # Ruta privada protegida por login
# @app.route('/privado')
# def privado():
#     if 'usuario' not in session:
#         return redirect(url_for('usuario_bp.login'))
#     return f"Bienvenido, {session['usuario']}!"

# if __name__ == "__main__":
#     app.run(debug=True)
