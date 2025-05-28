from flask import Flask, render_template, request, redirect, url_for, flash, make_response, send_file, session
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import csv
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import base64

# Set the correct template folder path
template_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'static'))

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
            database='chocopasion1',
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        print(f"Intento de login con email: {email}")  # Debug print
        
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT u.id_usuario, u.nombre, u.email, r.nombre_rol as rol 
            FROM usuarios u
            JOIN roles r ON u.id_rol = r.id_rol
            WHERE u.email = %s AND u.contraseña = %s
        """, (email, password))
        
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            print(f"Usuario autenticado: {usuario}")  # Debug print
            session.clear()  # Limpiamos la sesión antes de asignar nuevos valores
            session['usuario_id'] = usuario['id_usuario']
            session['rol'] = usuario['rol']
            print(f"Rol asignado en sesión: {session.get('rol')}")  # Debug print
            
            # Verificamos el rol específicamente
            if usuario['rol'].lower() == 'administrador':
                print("Redirigiendo a dashboard (admin)")  # Debug print
                return redirect(url_for('index'))
            else:
                print("Redirigiendo a home (empleado)")  # Debug print
                return redirect(url_for('home'))
        else:
            print("Credenciales inválidas")  # Debug print
            return render_template('usuario/login.html', error='Credenciales inválidas')
            
    return render_template('usuario/login.html')

# Nueva ruta para la página de inicio de empleados
@app.route('/home')
def home():
    if 'usuario_id' not in session:
        print("No hay usuario en sesión, redirigiendo a login")  # Debug print
        return redirect(url_for('login'))
    
    print(f"Rol en sesión al acceder a home: {session.get('rol')}")  # Debug print
    
    # Verificamos el rol específicamente
    if session.get('rol', '').lower() == 'administrador':
        print("Usuario es administrador, redirigiendo a dashboard")  # Debug print
        return redirect(url_for('index'))
        
    return render_template("home.html")

# Dashboard principal
@app.route('/')
def index():
    if 'usuario_id' not in session:
        print("No hay usuario en sesión, redirigiendo a login")  # Debug print
        return redirect(url_for('login'))
    
    print(f"Rol en sesión al acceder a index: {session.get('rol')}")  # Debug print
    
    # Verificamos el rol específicamente
    if session.get('rol', '').lower() != 'administrador':
        print("Usuario no es administrador, redirigiendo a producción")  # Debug print
        return redirect(url_for('produccion_index'))
        
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        # Obtener datos para el gráfico de producción por producto
        cursor.execute("""
            SELECT p.nombre, SUM(pr.cantidad) as total
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            GROUP BY p.id_producto, p.nombre
            ORDER BY total DESC
            LIMIT 5
        """)
        data = cursor.fetchall()
        labels = [row['nombre'] for row in data]
        values = [row['total'] for row in data]

        # Datos para el gráfico de producción diaria
        cursor.execute("""
            SELECT DATE(fecha) as dia, SUM(cantidad) as total
            FROM produccion
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(fecha)
            ORDER BY dia
        """)
        daily_data = cursor.fetchall()
        daily_labels = [row['dia'].strftime('%d/%m') for row in daily_data]
        daily_values = [row['total'] for row in daily_data]

        # Datos para estadísticas generales
        cursor.execute("SELECT COUNT(*) AS total FROM productos")
        total_productos = cursor.fetchone()['total'] or 0

        cursor.execute("SELECT COUNT(*) AS total FROM responsables")
        total_responsables = cursor.fetchone()['total'] or 0

        cursor.execute("SELECT COALESCE(SUM(cantidad), 0) AS total FROM produccion")
        total_produccion = cursor.fetchone()['total'] or 0

        # Obtener lista de productos para el filtro
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = cursor.fetchall()

        # Obtener lista de responsables para el filtro
        cursor.execute("SELECT * FROM responsables ORDER BY nombre, apellido")
        responsables = cursor.fetchall()

        # Obtener fecha actual y primer día del mes
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        primer_dia_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')

        return render_template(
            "dashboard/index.html",
            labels=labels,
            values=values,
            daily_labels=daily_labels,
            daily_values=daily_values,
            total_productos=total_productos,
            total_responsables=total_responsables,
            total_produccion=total_produccion,
            productos=productos,
            responsables=responsables,
            fecha_inicio=primer_dia_mes,
            fecha_fin=fecha_actual,
            producto_seleccionado="0",
            responsable_seleccionado="0",
            mostrar_resultados=False,
            responsables_labels=[],         # <-- Agrega esto
            responsables_values=[],         # <-- Y esto
            zip=zip
        )

    except Error as err:
        flash(f'Error al cargar el dashboard: {str(err)}', 'danger')
        return redirect(url_for('index'))
    finally:
        conn.close()

@app.route('/produccion')
def produccion_index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener todas las producciones con nombres de productos, presentaciones y responsables
        cursor.execute("""
            SELECT p.*, 
                   pr.nombre as producto,
                   pres.descripcion as presentacion,
                   GROUP_CONCAT(CONCAT(r.nombre, ' ', r.apellido) SEPARATOR ', ') as responsable_nombre
            FROM produccion p
            JOIN productos pr ON p.id_producto = pr.id_producto
            JOIN presentaciones pres ON p.id_presentacion = pres.id_presentacion
            LEFT JOIN produccion_responsable prr ON p.id_produccion = prr.id_produccion
            LEFT JOIN responsables r ON prr.id_responsable = r.id_responsable
            GROUP BY p.id_produccion
            ORDER BY p.fecha DESC
        """)
        producciones = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('produccion/index.html', producciones=producciones)
    except Exception as e:
        print(f"Error al obtener producciones: {str(e)}")
        flash('Error al cargar los registros de producción', 'danger')
        return redirect(url_for('home'))

# NUEVA FUNCIONALIDAD: Exportar producción a CSV
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

@app.route('/export/produccion/excel')
def export_produccion_excel():
    try:
        # Obtén los filtros desde la URL (GET)
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        producto_id = request.args.get('producto', '0')
        responsable_id = request.args.get('responsable', '0')

        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        # Aplica los mismos filtros que en dashboard_filtrar
        query = """
            SELECT pr.fecha, p.nombre AS producto, pre.descripcion AS presentacion, pr.cantidad,
                   GROUP_CONCAT(CONCAT(r.nombre, ' ', r.apellido) SEPARATOR ', ') AS responsables_nombres
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            JOIN presentaciones pre ON pr.id_presentacion = pre.id_presentacion
            LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
            LEFT JOIN responsables r ON prr.id_responsable = r.id_responsable
            WHERE 1=1
        """
        params = []
        if fecha_inicio:
            query += " AND pr.fecha >= %s"
            params.append(fecha_inicio)
        if fecha_fin:
            query += " AND pr.fecha <= %s"
            params.append(fecha_fin)
        if producto_id != '0':
            query += " AND pr.id_producto = %s"
            params.append(producto_id)
        if responsable_id != '0':
            query += " AND prr.id_responsable = %s"
            params.append(responsable_id)
        query += " GROUP BY pr.id_produccion ORDER BY pr.fecha DESC"

        cursor.execute(query, params)
        producciones = cursor.fetchall()
        conn.close()

        # Crear archivo Excel en memoria
        wb = Workbook()
        ws = wb.active
        ws.title = "Producción"

        # Escribir encabezados
        headers = ['FECHA', 'PRODUCTO', 'PRESENTACION', 'CANTIDAD', 'RESPONSABLES']
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')

        # Escribir datos filtrados
        for produccion in producciones:
            ws.append([
                produccion['fecha'].strftime('%Y-%m-%d') if produccion['fecha'] else '',
                produccion['producto'],
                produccion['presentacion'],
                produccion['cantidad'],
                produccion['responsables_nombres'] or ''
            ])

        # Ajustar ancho de columnas automáticamente
        for column_cells in ws.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = length + 2

        # Guardar en memoria
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        # Preparar respuesta
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=produccion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        return response

    except Exception as e:
        flash(f'Error al exportar Excel: {str(e)}', 'danger')
        return redirect(url_for('index'))
    
# NUEVA FUNCIONALIDAD: Exportar producción a PDF
@app.route('/export/produccion/pdf', methods=['POST'])
def export_produccion_pdf():
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        products_img = data.get('productsImg')
        daily_img = data.get('dailyImg')
        resp_img = data.get('respImg')

        # Procesa los filtros igual que en dashboard_filtrar
        fecha_inicio = filters.get('fecha_inicio')
        fecha_fin = filters.get('fecha_fin')
        producto_id = filters.get('producto', '0')
        responsable_id = filters.get('responsable', '0')

        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        # Consulta filtrada igual que en dashboard_filtrar
        query = """
            SELECT pr.fecha, p.nombre AS producto, pre.descripcion AS presentacion, pr.cantidad,
                   GROUP_CONCAT(CONCAT(r.nombre, ' ', r.apellido) SEPARATOR ', ') AS responsables_nombres
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            JOIN presentaciones pre ON pr.id_presentacion = pre.id_presentacion
            LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
            LEFT JOIN responsables r ON prr.id_responsable = r.id_responsable
            WHERE 1=1
        """
        params = []
        if fecha_inicio:
            query += " AND pr.fecha >= %s"
            params.append(fecha_inicio)
        if fecha_fin:
            query += " AND pr.fecha <= %s"
            params.append(fecha_fin)
        if producto_id and producto_id != "0":
            query += " AND pr.id_producto = %s"
            params.append(producto_id)
        if responsable_id and responsable_id != "0":
            query += " AND prr.id_responsable = %s"
            params.append(responsable_id)
        query += " GROUP BY pr.id_produccion ORDER BY pr.fecha DESC"

        cursor.execute(query, params)
        producciones = cursor.fetchall()
        conn.close()

        # Calcular total
        total_cantidad = sum(p['cantidad'] for p in producciones)

        # Crear PDF en memoria
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Título y filtros
        story.append(Paragraph("Reporte de Producción - ChocoPasión", styles['Title']))
        story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        if fecha_inicio or fecha_fin or producto_id != "0" or responsable_id != "0":
            filtros = f"<b>Filtros:</b> "
            if fecha_inicio: filtros += f"Desde {fecha_inicio} "
            if fecha_fin: filtros += f"Hasta {fecha_fin} "
            if producto_id != "0": filtros += f" | Producto ID: {producto_id} "
            if responsable_id != "0": filtros += f" | Responsable ID: {responsable_id} "
            story.append(Paragraph(filtros, styles['Normal']))
        story.append(Spacer(1, 12))

        # Agrega las imágenes de los gráficos
        from reportlab.platypus import Image
        import re

        def img_from_base64(data_url, width=500):
            if not data_url: return None
            header, encoded = data_url.split(",", 1)
            img_bytes = io.BytesIO(base64.b64decode(encoded))
            img = Image(img_bytes, width=width, height=width*0.5)
            img.hAlign = 'CENTER'
            return img

        for img_data, title in [
            (products_img, "Producción por Producto"),
            (daily_img, "Producción Diaria"),
            (resp_img, "Producción por Responsable")
        ]:
            if img_data:
                story.append(Paragraph(title, styles['Heading3']))
                img = img_from_base64(img_data)
                if img:
                    story.append(img)
                    story.append(Spacer(1, 12))

        # Resumen
        resumen = Paragraph(f"<b>Total de registros:</b> {len(producciones)}<br/><b>Cantidad total producida:</b> {total_cantidad}", styles['Normal'])
        story.append(resumen)
        story.append(Spacer(1, 20))

        # Tabla de datos
        if producciones:
            data = [['Fecha', 'Producto', 'Presentación', 'Cantidad', 'Responsables']]
            for produccion in producciones:
                data.append([
                    produccion['fecha'].strftime('%d/%m/%Y') if produccion['fecha'] else '',
                    produccion['producto'],
                    produccion['presentacion'],
                    str(produccion['cantidad']),
                    produccion['responsables_nombres'] or ''
                ])
            table = Table(data, colWidths=[1.2*inch, 1.8*inch, 1.5*inch, 0.8*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No hay datos de producción para mostrar.", styles['Normal']))

        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'produccion_filtrada_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error al exportar PDF: {str(e)}")
        return "Error al exportar PDF", 500


# Rutas para Producción
@app.route('/produccion/agregar', methods=['GET', 'POST'])
def produccion_agregar():
    if 'usuario_id' not in session:
        flash('Debe iniciar sesión para realizar esta acción', 'danger')
        return redirect(url_for('login'))

    rol = session.get('rol', '').lower()
    if rol not in ['administrador', 'empleado']:
        flash('No tiene permisos para realizar esta acción', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            conn = conectar()
            cursor = conn.cursor(dictionary=True)
            
            fecha = request.form['fecha']
            producto = request.form['producto']
            presentacion = request.form['presentacion']
            cantidad = request.form['cantidad']
            responsables = request.form.getlist('responsables[]')

            # Insertar producción
            cursor.execute("""
                INSERT INTO produccion (fecha, id_producto, id_presentacion, cantidad)
                VALUES (%s, %s, %s, %s)
            """, (fecha, producto, presentacion, cantidad))
            produccion_id = cursor.lastrowid

            # Insertar responsables en la tabla intermedia
            for responsable_id in responsables:
                cursor.execute("""
                    INSERT INTO produccion_responsable (id_produccion, id_responsable)
                    VALUES (%s, %s)
                """, (produccion_id, responsable_id))

            conn.commit()
            flash('Producción agregada exitosamente', 'success')
            return redirect(url_for('produccion_index'))
        except Exception as e:
            print(f"Error al agregar producción: {str(e)}")
            flash(f'Error al agregar producción: {str(e)}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('produccion_index'))

    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = cursor.fetchall()
        
        cursor.execute("SELECT * FROM presentaciones ORDER BY descripcion")
        presentaciones = cursor.fetchall()
        
        cursor.execute("SELECT * FROM responsables ORDER BY nombre")
        responsables = cursor.fetchall()
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        
        return render_template(
            "produccion/agregar.html",
            productos=productos,
            presentaciones=presentaciones,
            responsables=responsables,
            fecha_actual=fecha_actual
        )
    except Exception as e:
        print(f"Error al cargar formulario: {str(e)}")
        flash('Error al cargar el formulario', 'danger')
        return redirect(url_for('produccion_index'))
    finally:
        if conn:
            conn.close()

@app.route('/produccion/editar/<int:id>', methods=['GET', 'POST'])
def produccion_editar(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            fecha = request.form['fecha']
            producto = request.form['producto']
            presentacion = request.form['presentacion']
            cantidad = request.form['cantidad']
            responsables = request.form.getlist('responsables')

            # Actualizar producción
            cursor.execute("""
                UPDATE produccion
                SET fecha=%s, id_producto=%s, id_presentacion=%s, cantidad=%s
                WHERE id_produccion=%s
            """, (fecha, producto, presentacion, cantidad, id))

            # Eliminar responsables actuales
            cursor.execute(
                "DELETE FROM produccion_responsable WHERE id_produccion=%s", (id,))

            # Insertar nuevos responsables
            for responsable_id in responsables:
                cursor.execute("""
                    INSERT INTO produccion_responsable (id_produccion, id_responsable)
                    VALUES (%s, %s)
                """, (id, responsable_id))

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

    # Obtener responsables actuales
    cursor.execute(
        "SELECT id_responsable FROM produccion_responsable WHERE id_produccion=%s", (id,))
    responsables_ids = [str(row['id_responsable']) for row in cursor.fetchall()]

    conn.close()
    return render_template(
        "produccion/editar.html",
        produccion=produccion,
        productos=productos,
        presentaciones=presentaciones,
        usuarios=usuarios,
        responsables_ids=responsables_ids
    )

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

    # Obtener responsables
    cursor.execute("""
        SELECT u.id_responsable, u.nombre, u.apellido
        FROM produccion_responsable prr
        JOIN responsables u ON prr.id_responsable = u.id_responsable
        WHERE prr.id_produccion = %s
    """, (id,))
    responsables = cursor.fetchall()

    conn.close()
    return render_template("produccion/ver.html", produccion=produccion, responsables=responsables)

@app.route('/produccion/eliminar/<int:id>')
def produccion_eliminar(id):
    if 'usuario_id' not in session:
        flash('Debe iniciar sesión para realizar esta acción', 'danger')
        return redirect(url_for('login'))

    conn = conectar()
    cursor = conn.cursor()
    try:
        # Primero eliminamos los registros en la tabla intermedia
        cursor.execute("DELETE FROM produccion_responsable WHERE id_produccion = %s", (id,))
        
        # Luego eliminamos la producción
        cursor.execute("DELETE FROM produccion WHERE id_produccion = %s", (id,))
        
        conn.commit()
        flash('Producción eliminada exitosamente', 'success')
    except Error as err:
        conn.rollback()
        flash(f'Error al eliminar la producción: {str(err)}', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('produccion_index'))

# INFORMES
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
                   pr.cantidad,
                   GROUP_CONCAT(CONCAT(u.nombre, ' ', u.apellido) SEPARATOR ', ') AS responsables_nombres
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            JOIN presentaciones pre ON pr.id_presentacion = pre.id_presentacion
            LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
            LEFT JOIN usuarios u ON prr.id_usuario = u.id_usuario
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

        total_cantidad = sum(p['cantidad']
                             for p in producciones) if producciones else 0

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

# Rutas para Productos
@app.route('/productos')
def productos_index():
    if 'usuario_id' not in session:
        flash('Debe iniciar sesión para realizar esta acción', 'danger')
        return redirect(url_for('login'))
    
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()
    conn.close()
    
    # Si es empleado, mostrar la vista de lectura
    if session.get('rol', '').lower() == 'empleado':
        return render_template("producto/ver.html", productos=productos)
    
    # Si es administrador, mostrar la vista completa con opciones de CRUD
    return render_template("producto/index.html", productos=productos)

@app.route('/productos/agregar', methods=['GET', 'POST'])
def productos_agregar():
    if 'usuario_id' not in session:
        flash('Debe iniciar sesión para realizar esta acción', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            conn = conectar()
            cursor = conn.cursor()
            
            nombre = request.form['nombre']
            codigo = request.form.get('codigo', '')
            descripcion = request.form.get('descripcion', '')
            
            cursor.execute("""
                INSERT INTO productos (nombre, codigo, descripcion)
                VALUES (%s, %s, %s)
            """, (nombre, codigo, descripcion))
            
            conn.commit()
            flash('Producto creado exitosamente', 'success')
            return redirect(url_for('productos_index'))
        except Exception as e:
            flash(f'Error al crear el producto: {str(e)}', 'danger')
        finally:
            if conn:
                conn.close()
    
    return render_template("producto/agregar.html")

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def productos_editar(id):
    if 'usuario_id' not in session:
        flash('Debe iniciar sesión para realizar esta acción', 'danger')
        return redirect(url_for('login'))
    
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            codigo = request.form.get('codigo', '')
            descripcion = request.form.get('descripcion', '')
            
            cursor.execute("""
                UPDATE productos 
                SET nombre = %s, codigo = %s, descripcion = %s
                WHERE id_producto = %s
            """, (nombre, codigo, descripcion, id))
            
            conn.commit()
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('productos_index'))
        except Exception as e:
            flash(f'Error al actualizar el producto: {str(e)}', 'danger')
        finally:
            conn.close()

    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id,))
    producto = cursor.fetchone()
    conn.close()

    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('productos_index'))

    return render_template("producto/editar.html", producto=producto)

@app.route('/productos/<int:id>/delete')
def productos_delete(id):
    if 'usuario_id' not in session:
        flash('Debe iniciar sesión para realizar esta acción', 'danger')
        return redirect(url_for('login'))
    
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id,))
        conn.commit()
        flash('Producto eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el producto: {str(e)}', 'danger')
    finally:
        if conn:
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

    cursor.execute(
        "SELECT * FROM presentaciones WHERE id_presentacion=%s", (id,))
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
        cursor.execute(
            "SELECT COUNT(*) FROM produccion WHERE id_presentacion=%s", (id,))
        count = cursor.fetchone()[0]

        if count > 0:
            flash(
                'No se puede eliminar la presentación porque tiene producción asociada', 'danger')
        else:
            cursor.execute(
                "DELETE FROM presentaciones WHERE id_presentacion=%s", (id,))
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
    if 'usuario_id' not in session or session.get('rol') != 'administrador':
        return redirect(url_for('login'))
        
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
        cursor.execute(
            "SELECT COUNT(*) FROM produccion WHERE responsables LIKE %s", (f'%{id}%',))
        count = cursor.fetchone()[0]

        if count > 0:
            flash(
                'No se puede eliminar el usuario porque tiene producción asociada', 'danger')
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

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session or session.get('rol') != 'administrador':
        flash('Debe iniciar sesión como administrador para acceder al dashboard', 'danger')
        return redirect(url_for('login'))

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        # Obtener datos para el gráfico de producción por producto
        cursor.execute("""
            SELECT p.nombre, SUM(pr.cantidad) as total
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            GROUP BY p.id_producto, p.nombre
            ORDER BY total DESC
            LIMIT 5
        """)
        data = cursor.fetchall()
        labels = [row['nombre'] for row in data]
        values = [row['total'] for row in data]

        # Datos para el gráfico de producción diaria
        cursor.execute("""
            SELECT DATE(fecha) as dia, SUM(cantidad) as total
            FROM produccion
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(fecha)
            ORDER BY dia
        """)
        daily_data = cursor.fetchall()
        daily_labels = [row['dia'].strftime('%d/%m') for row in daily_data]
        daily_values = [row['total'] for row in daily_data]

        # Datos para estadísticas generales
        cursor.execute("SELECT COUNT(*) AS total FROM productos")
        total_productos = cursor.fetchone()['total'] or 0

        cursor.execute("SELECT COUNT(*) AS total FROM responsables")
        total_responsables = cursor.fetchone()['total'] or 0

        cursor.execute("SELECT COALESCE(SUM(cantidad), 0) AS total FROM produccion")
        total_produccion = cursor.fetchone()['total'] or 0

        # Obtener lista de productos para el filtro
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = cursor.fetchall()

        # Obtener lista de responsables para el filtro
        cursor.execute("SELECT * FROM responsables ORDER BY nombre, apellido")
        responsables = cursor.fetchall()

        # Obtener fecha actual y primer día del mes
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        primer_dia_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')

        return render_template(
            "dashboard/index.html",
            labels=labels,
            values=values,
            daily_labels=daily_labels,
            daily_values=daily_values,
            total_productos=total_productos,
            total_responsables=total_responsables,
            total_produccion=total_produccion,
            productos=productos,
            responsables=responsables,
            fecha_inicio=primer_dia_mes,
            fecha_fin=fecha_actual,
            producto_seleccionado="0",
            responsable_seleccionado="0",
            mostrar_resultados=False,
            responsables_labels=[],         # <-- Agrega esto
            responsables_values=[],         # <-- Y esto
            zip=zip
        )

    except Error as err:
        flash(f'Error al cargar el dashboard: {str(err)}', 'danger')
        return redirect(url_for('index'))
    finally:
        conn.close()

@app.route('/dashboard/filtrar', methods=['GET', 'POST'])
def dashboard_filtrar():
    if 'usuario_id' not in session or session.get('rol') != 'administrador':
        flash('Debe iniciar sesión como administrador para acceder al dashboard', 'danger')
        return redirect(url_for('login'))

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        # Obtener datos para el gráfico de producción por producto
        cursor.execute("""
            SELECT p.nombre, SUM(pr.cantidad) as total
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            GROUP BY p.id_producto, p.nombre
            ORDER BY total DESC
            LIMIT 5
        """)
        data = cursor.fetchall()
        labels = [row['nombre'] for row in data]
        values = [row['total'] for row in data]

        # Datos para el gráfico de producción diaria
        cursor.execute("""
            SELECT DATE(fecha) as dia, SUM(cantidad) as total
            FROM produccion
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(fecha)
            ORDER BY dia
        """)
        daily_data = cursor.fetchall()
        daily_labels = [row['dia'].strftime('%d/%m') for row in daily_data]
        daily_values = [row['total'] for row in daily_data]

        # Datos para estadísticas generales
        cursor.execute("SELECT COUNT(*) AS total FROM productos")
        total_productos = cursor.fetchone()['total'] or 0

        cursor.execute("SELECT COUNT(*) AS total FROM responsables")
        total_responsables = cursor.fetchone()['total'] or 0

        cursor.execute("SELECT COALESCE(SUM(cantidad), 0) AS total FROM produccion")
        total_produccion = cursor.fetchone()['total'] or 0

        # Obtener lista de productos para el filtro
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = cursor.fetchall()

        # Obtener lista de responsables para el filtro
        cursor.execute("SELECT * FROM responsables ORDER BY nombre, apellido")
        responsables = cursor.fetchall()

        # Obtener fecha actual y primer día del mes
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        primer_dia_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')

        # Obtener datos filtrados
        if request.method == 'POST':
            fecha_inicio = request.form.get('fecha_inicio', primer_dia_mes)
            fecha_fin = request.form.get('fecha_fin', fecha_actual)
            producto_id = request.form.get('producto', '0')
            responsable_id = request.form.get('responsable', '0')
        else:
            fecha_inicio = request.args.get('fecha_inicio', primer_dia_mes)
            fecha_fin = request.args.get('fecha_fin', fecha_actual)
            producto_id = request.args.get('producto', '0')
            responsable_id = request.args.get('responsable', '0')

        # Construir la consulta base
        query = """
            SELECT pr.fecha, p.nombre AS producto, pre.descripcion AS presentacion,
                pr.cantidad, GROUP_CONCAT(CONCAT(r.nombre, ' ', r.apellido) SEPARATOR ', ') AS responsables
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            JOIN presentaciones pre ON pr.id_presentacion = pre.id_presentacion
            LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
            LEFT JOIN responsables r ON prr.id_responsable = r.id_responsable
            WHERE 1=1
        """
        params = []

        if fecha_inicio:
            query += " AND pr.fecha >= %s"
            params.append(fecha_inicio)

        if fecha_fin:
            query += " AND pr.fecha <= %s"
            params.append(fecha_fin)

        if producto_id != '0':
            query += " AND pr.id_producto = %s"
            params.append(producto_id)

        if responsable_id != '0':
            query += " AND prr.id_responsable = %s"
            params.append(responsable_id)

        query += " GROUP BY pr.id_produccion ORDER BY pr.fecha DESC"

        cursor.execute(query, params)
        producciones = cursor.fetchall()
        mostrar_resultados = True

        # Obtener datos filtrados para la tabla y gráficos
        # ...ya tienes la consulta principal...

        # Nueva consulta para producción diaria filtrada
        daily_query = """
            SELECT DATE(pr.fecha) as dia, SUM(pr.cantidad) as total
            FROM produccion pr
            LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
            WHERE 1=1
        """
        daily_params = []

        if fecha_inicio:
            daily_query += " AND pr.fecha >= %s"
            daily_params.append(fecha_inicio)
        if fecha_fin:
            daily_query += " AND pr.fecha <= %s"
            daily_params.append(fecha_fin)
        if producto_id != '0':
            daily_query += " AND pr.id_producto = %s"
            daily_params.append(producto_id)
        if responsable_id != '0':
            daily_query += " AND prr.id_responsable = %s"
            daily_params.append(responsable_id)

        daily_query += " GROUP BY dia ORDER BY dia"

        cursor.execute(daily_query, daily_params)
        daily_data = cursor.fetchall()
        daily_labels = [row['dia'].strftime('%d/%m') for row in daily_data]
        daily_values = [row['total'] for row in daily_data]

        # Producción por responsable
        resp_query = """
            SELECT CONCAT(r.nombre, ' ', r.apellido) as responsable, SUM(pr.cantidad) as total
            FROM produccion pr
            LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
            LEFT JOIN responsables r ON prr.id_responsable = r.id_responsable
            WHERE 1=1
        """
        resp_params = []
        if fecha_inicio:
            resp_query += " AND pr.fecha >= %s"
            resp_params.append(fecha_inicio)
        if fecha_fin:
            resp_query += " AND pr.fecha <= %s"
            resp_params.append(fecha_fin)
        if producto_id != '0':
            resp_query += " AND pr.id_producto = %s"
            resp_params.append(producto_id)
        if responsable_id != '0':
            resp_query += " AND prr.id_responsable = %s"
            resp_params.append(responsable_id)
        resp_query += " GROUP BY responsable ORDER BY total DESC LIMIT 10"

        cursor.execute(resp_query, resp_params)
        resp_data = cursor.fetchall()
        responsables_labels = [row['responsable'] or 'Sin asignar' for row in resp_data]
        responsables_values = [row['total'] for row in resp_data]

        # Consulta para Top de Productos y Producción por Producto filtrados
        productos_query = """
            SELECT p.nombre, SUM(pr.cantidad) as total
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            JOIN presentaciones pre ON pr.id_presentacion = pre.id_presentacion
            LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
            LEFT JOIN responsables r ON prr.id_responsable = r.id_responsable
            WHERE 1=1
        """
        productos_params = []

        if fecha_inicio:
            productos_query += " AND pr.fecha >= %s"
            productos_params.append(fecha_inicio)
        if fecha_fin:
            productos_query += " AND pr.fecha <= %s"
            productos_params.append(fecha_fin)
        if producto_id != '0':
            productos_query += " AND pr.id_producto = %s"
            productos_params.append(producto_id)
        if responsable_id != '0':
            productos_query += " AND prr.id_responsable = %s"
            productos_params.append(responsable_id)

        productos_query += " GROUP BY p.id_producto, p.nombre ORDER BY total DESC LIMIT 5"

        cursor.execute(productos_query, productos_params)
        data = cursor.fetchall()
        labels = [row['nombre'] for row in data]
        values = [row['total'] for row in data]

        # 1. Obtener página actual desde GET o POST
        pagina_actual = int(request.args.get('pagina', 1))
        por_pagina = 10
        offset = (pagina_actual - 1) * por_pagina

        # 2. Consulta para contar el total de resultados filtrados
        count_query = """
            SELECT COUNT(DISTINCT pr.id_produccion) as total
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            JOIN presentaciones pre ON pr.id_presentacion = pre.id_presentacion
            LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
            LEFT JOIN responsables r ON prr.id_responsable = r.id_responsable
            WHERE 1=1
        """
        count_params = list(params)  # Usa los mismos filtros que tu consulta principal

        if fecha_inicio:
            count_query += " AND pr.fecha >= %s"
        if fecha_fin:
            count_query += " AND pr.fecha <= %s"
        if producto_id != '0':
            count_query += " AND pr.id_producto = %s"
        if responsable_id != '0':
            count_query += " AND prr.id_responsable = %s"

        cursor.execute(count_query, count_params)
        total_resultados = cursor.fetchone()['total']
        total_paginas = max(1, (total_resultados + por_pagina - 1) // por_pagina)

        # 3. Consulta principal con LIMIT y OFFSET
        query += f" LIMIT {por_pagina} OFFSET {offset}"
        cursor.execute(query, params)
        producciones = cursor.fetchall()

        # 4. Construir query_string para mantener filtros en la URL
        from urllib.parse import urlencode
        filtros = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'producto': producto_id,
            'responsable': responsable_id
        }
        query_string = urlencode({k: v for k, v in filtros.items() if v and v != '0'})

        # Consulta para producción total filtrada
        total_query = """
            SELECT SUM(pr.cantidad) as total
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            JOIN presentaciones pre ON pr.id_presentacion = pre.id_presentacion
            LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
            LEFT JOIN responsables r ON prr.id_responsable = r.id_responsable
            WHERE 1=1
        """
        total_params = []

        if fecha_inicio:
            total_query += " AND pr.fecha >= %s"
            total_params.append(fecha_inicio)
        if fecha_fin:
            total_query += " AND pr.fecha <= %s"
            total_params.append(fecha_fin)
        if producto_id != '0':
            total_query += " AND pr.id_producto = %s"
            total_params.append(producto_id)
        if responsable_id != '0':
            total_query += " AND prr.id_responsable = %s"
            total_params.append(responsable_id)

        cursor.execute(total_query, total_params)
        total_produccion_filtrada = cursor.fetchone()['total'] or 0

        return render_template(
            "dashboard/index.html",
            labels=labels,
            values=values,
            daily_labels=daily_labels,
            daily_values=daily_values,
            total_productos=total_productos,
            total_responsables=total_responsables,
            total_produccion=total_produccion_filtrada,
            productos=productos,
            responsables=responsables,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            producto_seleccionado=producto_id,
            responsable_seleccionado=responsable_id,
            mostrar_resultados=mostrar_resultados,
            producciones=producciones,
            responsables_labels=responsables_labels,
            responsables_values=responsables_values,
            pagina_actual=pagina_actual,
            total_paginas=total_paginas,
            query_string=query_string,
            zip=zip
        )

    except Error as err:
            flash(f'Error al cargar el dashboard: {str(err)}', 'danger')
            return redirect(url_for('index'))
    finally:
            conn.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)