from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
import os

# Set the correct template folder path
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

# Initialize Flask with the correct template and static folders
app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)

def conectar():
    try:
        print("Intentando conectar a la base de datos...")
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='chocopasion',
            port=3306,
            auth_plugin='mysql_native_password'
        )
        print("✅ Conexión exitosa a la base de datos")
        return conn
    except Error as err:
        print(f"❌ Error al conectar a la base de datos: {err}")
        if err.errno == 1045:
            print("Error: Usuario o contraseña incorrectos")
        elif err.errno == 1049:
            print("Error: La base de datos no existe")
        elif err.errno == 2003:
            print("Error: No se puede conectar al servidor MySQL")
        raise

# Dashboard principal
@app.route('/')
def index():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.nombre AS producto, SUM(pr.cantidad) AS total
        FROM produccion pr
        JOIN productos p ON pr.id_producto = p.id_producto
        GROUP BY p.nombre
    """)
    data = cursor.fetchall()
    labels = [row['producto'] for row in data]
    values = [row['total'] for row in data]
    conn.close()
    print("Renderizando dashboard/index.html")
    print(f"Template folder: {template_dir}")
    print(f"Template file exists: {os.path.exists(os.path.join(template_dir, 'dashboard', 'index.html'))}")
    return render_template("dashboard/index.html", labels=labels, values=values)

# Rutas para Producción
@app.route('/produccion')
def produccion_index():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT pr.*, p.nombre AS producto, pre.descripcion AS presentacion
        FROM produccion pr
        JOIN productos p ON pr.id_producto = p.id_producto
        JOIN presentaciones pre ON pr.id_presentacion = pre.id_presentacion
    """)
    producciones = cursor.fetchall()
    conn.close()
    return render_template("produccion/index.html", producciones=producciones)

@app.route('/produccion/agregar', methods=['GET', 'POST'])
def produccion_agregar():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        responsables = ','.join(request.form.getlist('responsables'))
        cursor.execute("""
            INSERT INTO produccion (fecha, id_producto, id_presentacion, cantidad, responsables)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form['fecha'],
            request.form['producto'],
            request.form['presentacion'],
            request.form['cantidad'],
            responsables
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('produccion_index'))
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.execute("SELECT * FROM presentaciones")
    presentaciones = cursor.fetchall()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template("produccion/agregar.html", productos=productos, presentaciones=presentaciones, usuarios=usuarios)

@app.route('/produccion/editar/<int:id>', methods=['GET', 'POST'])
def produccion_editar(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        responsables = ','.join(request.form.getlist('responsables'))
        cursor.execute("""
            UPDATE produccion
            SET fecha=%s, id_producto=%s, id_presentacion=%s, cantidad=%s, responsables=%s
            WHERE id_produccion=%s
        """, (
            request.form['fecha'],
            request.form['producto'],
            request.form['presentacion'],
            request.form['cantidad'],
            responsables,
            id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('produccion_index'))
    cursor.execute("SELECT * FROM produccion WHERE id_produccion=%s", (id,))
    produccion = cursor.fetchone()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.execute("SELECT * FROM presentaciones")
    presentaciones = cursor.fetchall()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template("produccion/editar.html", produccion=produccion, productos=productos, presentaciones=presentaciones, usuarios=usuarios)

@app.route('/produccion/eliminar/<int:id>', methods=['GET', 'POST'])
def produccion_eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produccion WHERE id_produccion=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('produccion_index'))

# Rutas para Productos
@app.route('/productos')
def productos_index():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template("producto/index.html", productos=productos)

@app.route('/productos/agregar', methods=['GET', 'POST'])
def productos_agregar():
    if request.method == 'POST':
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (codigo, nombre) VALUES (%s, %s)", 
                       (request.form['codigo'], request.form['nombre']))
        conn.commit()
        conn.close()
        return redirect(url_for('productos_index'))
    return render_template("producto/agregar.html")

@app.route('/productos/eliminar/<int:id>')
def productos_eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('productos_index'))

# Rutas para Usuarios
@app.route('/usuarios')
def usuarios_index():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template("usuario/index.html", usuarios=usuarios)

@app.route('/usuarios/agregar', methods=['GET', 'POST'])
def usuarios_agregar():
    if request.method == 'POST':
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, apellido, email) VALUES (%s, %s, %s)", 
                       (request.form['nombre'], request.form['apellido'], request.form['email']))
        conn.commit()
        conn.close()
        return redirect(url_for('usuarios_index'))
    return render_template("usuario/agregar.html")

@app.route('/usuarios/eliminar/<int:id>')
def usuarios_eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('usuarios_index'))

if __name__ == '__main__':
    app.run(debug=True)