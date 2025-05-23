from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime

# Set the correct template folder path
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

# Initialize Flask with the correct template and static folders
app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)

# Secret key for session management and flash messages
app.secret_key = 'chocopasion_secretkey'

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
    
    # Datos para el gráfico de producción por producto
    cursor.execute("""
        SELECT p.nombre AS producto, SUM(pr.cantidad) AS total
        FROM produccion pr
        JOIN productos p ON pr.id_producto = p.id_producto
        GROUP BY p.nombre
    """)
    data = cursor.fetchall()
    labels = [row['producto'] for row in data]
    values = [row['total'] for row in data]
    
    # Datos para estadísticas generales
    cursor.execute("SELECT COUNT(*) AS total FROM productos")
    total_productos = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
    total_usuarios = cursor.fetchone()['total']
    
    cursor.execute("SELECT SUM(cantidad) AS total FROM produccion")
    total_produccion = cursor.fetchone()['total'] or 0
    
    # Últimas producciones
    cursor.execute("""
        SELECT pr.fecha, p.nombre AS producto, pre.descripcion AS presentacion, pr.cantidad
        FROM produccion pr
        JOIN productos p ON pr.id_producto = p.id_producto
        JOIN presentaciones pre ON pr.id_presentacion = pre.id_presentacion
        ORDER BY pr.fecha DESC
        LIMIT 5
    """)
    ultimas_producciones = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        "dashboard/index.html", 
        labels=labels, 
        values=values,
        zip=zip,  # Añadimos zip para usarlo en las plantillas
        total_productos=total_productos,
        total_usuarios=total_usuarios,
        total_produccion=total_produccion,
        ultimas_producciones=ultimas_producciones
    )

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
        ORDER BY pr.fecha DESC
    """)
    producciones = cursor.fetchall()
    conn.close()
    return render_template("produccion/index.html", producciones=producciones)

@app.route('/produccion/agregar', methods=['GET', 'POST'])
def produccion_agregar():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            # Obtén los datos del formulario
            fecha = request.form['fecha']
            producto = request.form['producto']
            presentacion = request.form['presentacion']
            cantidad = request.form['cantidad']
            responsables = request.form.getlist('responsables')  # Obtiene todos los responsables seleccionados

            # Inserta los datos en la tabla `produccion`
            cursor.execute("""
                INSERT INTO produccion (fecha, id_producto, id_presentacion, cantidad)
                VALUES (%s, %s, %s, %s)
            """, (fecha, producto, presentacion, cantidad))
            produccion_id = cursor.lastrowid  # Obtén el ID de la producción recién insertada

            # Inserta los responsables en la tabla `produccion_responsables`
            for responsable_id in responsables:
                cursor.execute("""
                    INSERT INTO produccion_responsables (produccion_id, responsable_id)
                    VALUES (%s, %s)
                """, (produccion_id, responsable_id))

            conn.commit()
            flash('Producción agregada exitosamente', 'success')
        except Error as err:
            # Imprime el error para depuración
            print(f"Error al agregar producción: {err}")
            flash(f'Error al agregar producción: {err}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('produccion_index'))
    
    # Carga los datos necesarios para el formulario
    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()
    cursor.execute("SELECT * FROM presentaciones ORDER BY descripcion")
    presentaciones = cursor.fetchall()
    cursor.execute("SELECT * FROM usuarios ORDER BY nombre")
    usuarios = cursor.fetchall()
    conn.close()
    
    # Fecha actual para el formulario
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    
    return render_template(
        "produccion/agregar.html", 
        productos=productos, 
        presentaciones=presentaciones, 
        usuarios=usuarios,
        fecha_actual=fecha_actual
    )
@app.route('/produccion/editar/<int:id>', methods=['GET', 'POST'])
def produccion_editar(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
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
            flash('Producción actualizada exitosamente', 'success')
        except Error as err:
            flash(f'Error al actualizar producción: {err}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('produccion_index'))
    
    cursor.execute("SELECT * FROM produccion WHERE id_produccion=%s", (id,))
    produccion = cursor.fetchone()
    
    if not produccion:
        conn.close()
        flash('Producción no encontrada', 'danger')
        return redirect(url_for('produccion_index'))
    
    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()
    cursor.execute("SELECT * FROM presentaciones ORDER BY descripcion")
    presentaciones = cursor.fetchall()
    cursor.execute("SELECT * FROM usuarios ORDER BY nombre")
    usuarios = cursor.fetchall()
    
    # Obtener lista de responsables
    responsables_ids = produccion['responsables'].split(',') if produccion['responsables'] else []
    
    conn.close()
    return render_template(
        "produccion/editar.html", 
        produccion=produccion, 
        productos=productos, 
        presentaciones=presentaciones, 
        usuarios=usuarios,
        responsables_ids=responsables_ids
    )

@app.route('/produccion/eliminar/<int:id>')
def produccion_eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM produccion WHERE id_produccion=%s", (id,))
        conn.commit()
        flash('Producción eliminada exitosamente', 'success')
    except Error as err:
        flash(f'Error al eliminar producción: {err}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('produccion_index'))

@app.route('/produccion/ver/<int:id>')
def produccion_ver(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT pr.*, p.nombre AS producto, p.codigo AS codigo_producto, pre.descripcion AS presentacion
        FROM produccion pr
        JOIN productos p ON pr.id_producto = p.id_producto
        JOIN presentaciones pre ON pr.id_presentacion = pre.id_presentacion
        WHERE pr.id_produccion = %s
    """, (id,))
    produccion = cursor.fetchone()
    
    if not produccion:
        conn.close()
        flash('Producción no encontrada', 'danger')
        return redirect(url_for('produccion_index'))
    
    # Obtener nombres de responsables
    if produccion['responsables']:
        responsables_ids = produccion['responsables'].split(',')
        placeholders = ','.join(['%s'] * len(responsables_ids))
        cursor.execute(f"SELECT id_usuario, nombre, apellido FROM usuarios WHERE id_usuario IN ({placeholders})", 
                      responsables_ids)
        responsables = cursor.fetchall()
    else:
        responsables = []
    
    conn.close()
    return render_template("produccion/ver.html", produccion=produccion, responsables=responsables)

# Rutas para Productos
@app.route('/productos')
def productos_index():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()
    conn.close()
    return render_template("producto/index.html", productos=productos)

# ...existing code...

@app.route('/productos/agregar', methods=['GET', 'POST'])
def productos_agregar():
    if request.method == 'POST':
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO productos (codigo, nombre, descripcion) VALUES (%s, %s, %s)", 
                (request.form['codigo'], request.form['nombre'], request.form['descripcion'])
            )
            conn.commit()
            flash('Producto agregado exitosamente', 'success')
        except Error as err:
            flash(f'Error al agregar producto: {err}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('productos_index'))
    return render_template("producto/agregar.html")

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def productos_editar(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE productos 
                SET codigo=%s, nombre=%s, descripcion=%s
                WHERE id_producto=%s
            """, (
                request.form['codigo'],
                request.form['nombre'],
                request.form['descripcion'],
                id
            ))
            conn.commit()
            flash('Producto actualizado exitosamente', 'success')
        except Error as err:
            flash(f'Error al actualizar producto: {err}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('productos_index'))
    
    cursor.execute("SELECT * FROM productos WHERE id_producto=%s", (id,))
    producto = cursor.fetchone()
    
    if not producto:
        conn.close()
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('productos_index'))
    
    conn.close()
    return render_template("producto/editar.html", producto=producto)


@app.route('/productos/eliminar/<int:id>')
def productos_eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Primero verificamos si hay producción asociada
        cursor.execute("SELECT COUNT(*) FROM produccion WHERE id_producto=%s", (id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            flash('No se puede eliminar el producto porque tiene producción asociada', 'danger')
        else:
            cursor.execute("DELETE FROM productos WHERE id_producto=%s", (id,))
            conn.commit()
            flash('Producto eliminado exitosamente', 'success')
    except Error as err:
        flash(f'Error al eliminar producto: {err}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('productos_index'))

# Rutas para Presentaciones
@app.route('/presentaciones')
def presentaciones_index():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM presentaciones ORDER BY descripcion")
    presentaciones = cursor.fetchall()
    conn.close()
    return render_template("presentacion/index.html", presentaciones=presentaciones)

@app.route('/presentaciones/agregar', methods=['GET', 'POST'])
def presentaciones_agregar():
    if request.method == 'POST':
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO presentaciones (descripcion) VALUES (%s)", 
                         (request.form['descripcion'],))
            conn.commit()
            flash('Presentación agregada exitosamente', 'success')
        except Error as err:
            flash(f'Error al agregar presentación: {err}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('presentaciones_index'))
    return render_template("presentacion/agregar.html")

@app.route('/presentaciones/editar/<int:id>', methods=['GET', 'POST'])
def presentaciones_editar(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE presentaciones 
                SET descripcion=%s
                WHERE id_presentacion=%s
            """, (
                request.form['descripcion'],
                id
            ))
            conn.commit()
            flash('Presentación actualizada exitosamente', 'success')
        except Error as err:
            flash(f'Error al actualizar presentación: {err}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('presentaciones_index'))
    
    cursor.execute("SELECT * FROM presentaciones WHERE id_presentacion=%s", (id,))
    presentacion = cursor.fetchone()
    
    if not presentacion:
        conn.close()
        flash('Presentación no encontrada', 'danger')
        return redirect(url_for('presentaciones_index'))
    
    conn.close()
    return render_template("presentacion/editar.html", presentacion=presentacion)

@app.route('/presentaciones/eliminar/<int:id>')
def presentaciones_eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Primero verificamos si hay producción asociada
        cursor.execute("SELECT COUNT(*) FROM produccion WHERE id_presentacion=%s", (id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            flash('No se puede eliminar la presentación porque tiene producción asociada', 'danger')
        else:
            cursor.execute("DELETE FROM presentaciones WHERE id_presentacion=%s", (id,))
            conn.commit()
            flash('Presentación eliminada exitosamente', 'success')
    except Error as err:
        flash(f'Error al eliminar presentación: {err}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('presentaciones_index'))

# Rutas para Usuarios
@app.route('/usuarios')
def usuarios_index():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios ORDER BY nombre, apellido")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template("usuario/index.html", usuarios=usuarios)

@app.route('/usuarios/agregar', methods=['GET', 'POST'])
def usuarios_agregar():
    if request.method == 'POST':
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (nombre, apellido, email) VALUES (%s, %s, %s)", 
                         (request.form['nombre'], request.form['apellido'], request.form['email']))
            conn.commit()
            flash('Usuario agregado exitosamente', 'success')
        except Error as err:
            flash(f'Error al agregar usuario: {err}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('usuarios_index'))
    return render_template("usuario/agregar.html")

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def usuarios_editar(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE usuarios 
                SET nombre=%s, apellido=%s, email=%s
                WHERE id_usuario=%s
            """, (
                request.form['nombre'],
                request.form['apellido'],
                request.form['email'],
                id
            ))
            conn.commit()
            flash('Usuario actualizado exitosamente', 'success')
        except Error as err:
            flash(f'Error al actualizar usuario: {err}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('usuarios_index'))
    
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=%s", (id,))
    usuario = cursor.fetchone()
    
    if not usuario:
        conn.close()
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('usuarios_index'))
    
    conn.close()
    return render_template("usuario/editar.html", usuario=usuario)

@app.route('/usuarios/eliminar/<int:id>')
def usuarios_eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Primero verificamos si hay producción asociada
        cursor.execute("SELECT COUNT(*) FROM produccion WHERE responsables LIKE %s", (f'%{id}%',))
        count = cursor.fetchone()[0]
        
        if count > 0:
            flash('No se puede eliminar el usuario porque tiene producción asociada', 'danger')
        else:
            cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id,))
            conn.commit()
            flash('Usuario eliminado exitosamente', 'success')
    except Error as err:
        flash(f'Error al eliminar usuario: {err}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('usuarios_index'))

# Informes y reportes
@app.route('/informes')
def informes_index():
    return render_template("informes/index.html")

@app.route('/informes/produccion', methods=['GET', 'POST'])
def informes_produccion():
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        producto = request.form.get('producto')
        
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT pr.fecha, p.nombre AS producto, pre.descripcion AS presentacion, 
                   pr.cantidad, GROUP_CONCAT(CONCAT(u.nombre, ' ', u.apellido) SEPARATOR ', ') AS responsables_nombres
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            JOIN presentaciones pre ON pr.id_presentacion = pre.id_presentacion
            LEFT JOIN usuarios u ON FIND_IN_SET(u.id_usuario, pr.responsables)
            WHERE 1=1
        """
        params = []
        
        if fecha_inicio:
            query += " AND pr.fecha >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND pr.fecha <= %s"
            params.append(fecha_fin)
        
        if producto and producto != "0":
            query += " AND pr.id_producto = %s"
            params.append(producto)
        
        query += " GROUP BY pr.id_produccion ORDER BY pr.fecha DESC"
        
        cursor.execute(query, params)
        producciones = cursor.fetchall()
        
        # Calcular totales
        total_cantidad = sum(p['cantidad'] for p in producciones) if producciones else 0
        
        # Obtener productos para el formulario
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = cursor.fetchall()
        
        conn.close()
        
        return render_template(
            "informes/produccion.html", 
            producciones=producciones,
            productos=productos,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            producto_seleccionado=producto,
            total_cantidad=total_cantidad,
            mostrar_resultados=True
        )
    else:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = cursor.fetchall()
        conn.close()
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        primer_dia_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        
        return render_template(
            "informes/produccion.html", 
            productos=productos,
            fecha_inicio=primer_dia_mes,
            fecha_fin=fecha_actual,
            mostrar_resultados=False
        )

if __name__ == '__main__':
    app.run(debug=True)