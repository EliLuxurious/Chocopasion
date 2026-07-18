from flask import Flask, render_template, request, redirect, url_for, flash, make_response, send_file, session, jsonify
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
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (si existe)
load_dotenv()

# Agregar el directorio padre al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar el blueprint de precios
from modules.precios.controller import precios_bp

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
app.secret_key = os.getenv('SECRET_KEY', 'chocopasion_dev_secret_2024')

# Registrar el blueprint de precios
app.register_blueprint(precios_bp, url_prefix='/precios')

def conectar():
    """Conecta a MySQL usando variables de entorno (Docker) o valores locales por defecto."""
    try:
        host     = os.getenv('MYSQL_HOST', '127.0.0.1')
        user     = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', '')
        database = os.getenv('MYSQL_DATABASE', 'chocopasion2')
        port     = int(os.getenv('MYSQL_PORT', 3306))

        print(f"Intentando conectar a la base de datos en {host}:{port}...")
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
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

def get_pagination_range(page, total_pages):
    """Generates a list of page numbers and ellipsis to show in pagination."""
    if total_pages <= 10:
        return list(range(1, total_pages + 1))
    
    # Otherwise, build pagination with ellipsis
    pages = []
    if page <= 6:
        # Show first 8 pages, then '...', then last page
        pages = list(range(1, 9)) + ['...', total_pages]
    elif page > total_pages - 6:
        # Show page 1, then '...', then last 8 pages
        pages = [1, '...'] + list(range(total_pages - 7, total_pages + 1))
    else:
        # Show page 1, then '...', then current_page-3 to current_page+3, then '...', then last page
        pages = [1, '...'] + list(range(page - 3, page + 4)) + ['...', total_pages]
    return pages

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
            WHERE u.email = %s AND u.contrasena = %s
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

        # Total producción con filtro de 30 días para consistencia
        cursor.execute("SELECT COALESCE(SUM(cantidad), 0) AS total FROM produccion WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
        total_produccion = cursor.fetchone()['total'] or 0
        
        print(f"🔍 DASHBOARD INICIAL - Total producción (30 días): {total_produccion}")

        # Obtener lista de productos para el filtro
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = cursor.fetchall()

        # Obtener lista de responsables para el filtro
        cursor.execute("SELECT * FROM responsables ORDER BY nombre, apellido")
        responsables = cursor.fetchall()

        # Obtener fecha actual y primer día del mes
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        primer_dia_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')

        # Datos para gráfico de producción por responsable
        try:
            cursor.execute("""
                SELECT 
                    CONCAT(r.nombre, ' ', r.apellido) as responsable,
                    SUM(pr.cantidad) as total
                FROM produccion pr
                JOIN produccion_responsable pro_resp ON pr.id_produccion = pro_resp.id_produccion
                JOIN responsables r ON pro_resp.id_responsable = r.id_responsable
                GROUP BY r.id_responsable, r.nombre, r.apellido
                ORDER BY total DESC
                LIMIT 5
            """)
            responsables_data = cursor.fetchall()
            responsables_labels = [row['responsable'] for row in responsables_data]
            responsables_values = [row['total'] for row in responsables_data]
        except:
            responsables_labels = []
            responsables_values = []

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
            zip=zip,
            responsables_labels=responsables_labels,
            responsables_values=responsables_values
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
        page = request.args.get('page', 1, type=int)
        if page < 1:
            page = 1
        limit = 10
        offset = (page - 1) * limit

        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener el total de registros de producción
        cursor.execute("SELECT COUNT(*) as total FROM produccion")
        total_count = cursor.fetchone()['total']
        total_pages = max(1, (total_count + limit - 1) // limit)

        # Obtener las producciones de la página actual con nombres de productos, presentaciones y responsables
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
            LIMIT %s OFFSET %s
        """, (limit, offset))
        producciones = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('produccion/index.html', 
                               producciones=producciones, 
                               page=page, 
                               total_pages=total_pages,
                               pages_range=get_pagination_range(page, total_pages))
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

        # Consulta filtrada igual que in dashboard_filtrar
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
            productos = request.form.getlist('productos[]')
            presentaciones = request.form.getlist('presentaciones[]')
            cantidades = request.form.getlist('cantidades[]')
            responsables = request.form.getlist('responsables[]')

            # Si no hay productos en la lista, intentar leer los campos tradicionales por compatibilidad
            if not productos:
                producto_single = request.form.get('producto')
                presentacion_single = request.form.get('presentacion')
                cantidad_single = request.form.get('cantidad')
                if producto_single and presentacion_single and cantidad_single:
                    productos = [producto_single]
                    presentaciones = [presentacion_single]
                    cantidades = [cantidad_single]

            registros_guardados = 0

            for i in range(len(productos)):
                prod_id = productos[i]
                pres_id = presentaciones[i]
                cant = cantidades[i]

                if not prod_id or not pres_id or not cant:
                    continue

                # Insertar producción
                cursor.execute("""
                    INSERT INTO produccion (fecha, id_producto, id_presentacion, cantidad)
                    VALUES (%s, %s, %s, %s)
                """, (fecha, prod_id, pres_id, cant))
                produccion_id = cursor.lastrowid

                # Insertar responsables en la tabla intermedia
                for responsable_id in responsables:
                    cursor.execute("""
                        INSERT INTO produccion_responsable (id_produccion, id_responsable)
                        VALUES (%s, %s)
                    """, (produccion_id, responsable_id))
                
                registros_guardados += 1

            conn.commit()
            if registros_guardados > 0:
                flash(f'Se registraron {registros_guardados} producciones exitosamente', 'success')
            else:
                flash('No se especificaron productos válidos para registrar', 'warning')
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
    
    try:
        page = request.args.get('page', 1, type=int)
        if page < 1:
            page = 1
        limit = 10
        offset = (page - 1) * limit

        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener el total de productos
        cursor.execute("SELECT COUNT(*) as total FROM productos")
        total_count = cursor.fetchone()['total']
        total_pages = max(1, (total_count + limit - 1) // limit)

        # Obtener los productos de la página actual
        cursor.execute("SELECT * FROM productos ORDER BY nombre LIMIT %s OFFSET %s", (limit, offset))
        productos = cursor.fetchall()
        conn.close()
        
        # Si es empleado, mostrar la vista de lectura
        if session.get('rol', '').lower() == 'empleado':
            return render_template("producto/ver.html", 
                                   productos=productos, 
                                   page=page, 
                                   total_pages=total_pages,
                                   pages_range=get_pagination_range(page, total_pages))
        
        # Si es administrador, mostrar la vista completa con opciones de CRUD
        return render_template("producto/index.html", 
                               productos=productos, 
                               page=page, 
                               total_pages=total_pages,
                               pages_range=get_pagination_range(page, total_pages))
    except Exception as e:
        print(f"Error al obtener productos: {str(e)}")
        flash('Error al cargar la lista de productos', 'danger')
        return redirect(url_for('home'))

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

        # CORREGIDO: Total producción con filtro de 30 días para consistencia
        cursor.execute("SELECT COALESCE(SUM(cantidad), 0) AS total FROM produccion WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
        total_produccion = cursor.fetchone()['total'] or 0
        
        print(f"🔍 DASHBOARD INICIAL - Total producción (30 días): {total_produccion}")

        # Obtener lista de productos para el filtro
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = cursor.fetchall()

        # Obtener lista de responsables para el filtro
        cursor.execute("SELECT * FROM responsables ORDER BY nombre, apellido")
        responsables = cursor.fetchall()

        # Obtener fecha actual y primer día del mes
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        primer_dia_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')

        # CONSULTAS PARA VENTAS - SIMPLIFICADAS CON FILTROS DE FECHA
        print("🔍 Iniciando consultas de ventas...")
        
        # Verificar datos duplicados
        try:
            cursor.execute("SELECT COUNT(*) as total_ventas FROM ventas")
            total_registros_ventas = cursor.fetchone()['total_ventas']
            cursor.execute("SELECT COUNT(DISTINCT id_venta) as ventas_unicas FROM ventas")
            ventas_unicas = cursor.fetchone()['ventas_unicas']
            print(f"📊 Total registros ventas: {total_registros_ventas}, Únicos: {ventas_unicas}")
            
            if total_registros_ventas != ventas_unicas:
                print("⚠️ ADVERTENCIA: Hay posibles duplicados en la tabla ventas")
        except Exception as e:
            print(f"❌ Error verificando duplicados: {e}")
        
        # Ventas por producto - CONSULTA DIRECTA SIN JOINS COMPLEJOS
        try:
            print("📊 Ejecutando consulta DIRECTA de ventas por producto...")
            cursor.execute("""
                SELECT 
                    p.nombre, 
                    (SELECT COALESCE(SUM(v.cantidad), 0) 
                     FROM ventas v 
                     WHERE v.id_producto = p.id_producto 
                     AND v.fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)) as total_vendido
                FROM productos p
                HAVING total_vendido > 0
                ORDER BY total_vendido DESC
                LIMIT 5
            """)
            ventas_data = cursor.fetchall()
            ventas_labels = [row['nombre'] for row in ventas_data]
            ventas_values = [int(row['total_vendido']) for row in ventas_data]
            
            print(f"✅ Ventas por producto (consulta directa): {len(ventas_data)} resultados")
            print(f"📋 Labels: {ventas_labels}")
            print(f"📋 Cantidades EXACTAS: {ventas_values}")
            
            # Verificación adicional - mostrar registros individuales para el primer producto
            if ventas_labels:
                cursor.execute("""
                    SELECT fecha, cantidad, total 
                    FROM ventas v 
                    JOIN productos p ON v.id_producto = p.id_producto 
                    WHERE p.nombre = %s 
                    AND v.fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    ORDER BY fecha DESC
                    LIMIT 5
                """, (ventas_labels[0],))
                registros_ejemplo = cursor.fetchall()
                print(f"🔍 Registros individuales para '{ventas_labels[0]}':")
                for reg in registros_ejemplo:
                    print(f"   📅 {reg['fecha']}: {reg['cantidad']} unidades, ${reg['total']}")
                    
        except Exception as e:
            print(f"❌ Error en ventas por producto: {e}")
            ventas_labels = []
            ventas_values = []

        # Ventas diarias (últimos 7 días) - CORREGIDA
        try:
            print("📅 Ejecutando consulta de ventas diarias corregida...")
            cursor.execute("""
                SELECT DATE(fecha) as dia, SUM(cantidad) as total_vendido_dia
                FROM ventas
                WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY DATE(fecha)
                ORDER BY dia
            """)
            ventas_diarias_data = cursor.fetchall()
            ventas_diarias_labels = [row['dia'].strftime('%d/%m') for row in ventas_diarias_data]
            ventas_diarias_values = [int(row['total_vendido_dia']) for row in ventas_diarias_data]  # Convertir a int
            print(f"✅ Ventas diarias: {len(ventas_diarias_data)} resultados")
            print(f"📋 Labels diarias: {ventas_diarias_labels}")
            print(f"📋 Cantidades diarias: {ventas_diarias_values}")
        except Exception as e:
            print(f"❌ Error en ventas diarias: {e}")
            ventas_diarias_labels = []
            ventas_diarias_values = []

        # Ingresos por producto - CON FILTRO DE FECHA
        try:
            print("💰 Ejecutando consulta de ingresos...")
            cursor.execute("""
                SELECT p.nombre, SUM(v.total) as ingresos
                FROM ventas v
                JOIN productos p ON v.id_producto = p.id_producto
                WHERE v.fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY p.id_producto, p.nombre
                ORDER BY ingresos DESC
                LIMIT 5
            """)
            ingresos_data = cursor.fetchall()
            ingresos_labels = [row['nombre'] for row in ingresos_data]
            ingresos_values = [float(row['ingresos']) for row in ingresos_data]
            print(f"✅ Ingresos (último mes): {len(ingresos_data)} resultados")
            print(f"📋 Ingresos labels: {ingresos_labels}")
        except Exception as e:
            print(f"❌ Error en ingresos por producto: {e}")
            ingresos_labels = []
            ingresos_values = []

        # Comparativa producción vs ventas por producto - CORREGIDA CON FECHA
        try:
            print("⚖️ Ejecutando consulta comparativa corregida con filtro de fecha...")
            
            # Obtener fecha del último mes para evitar multiplicaciones
            cursor.execute("SELECT DATE_SUB(CURDATE(), INTERVAL 30 DAY) as fecha_limite")
            fecha_limite = cursor.fetchone()['fecha_limite']
            
            # Primero obtenemos la producción por producto (último mes)
            cursor.execute("""
                SELECT 
                    p.id_producto,
                    p.nombre,
                    COALESCE(SUM(pr.cantidad), 0) as produccion_total
                FROM productos p
                LEFT JOIN produccion pr ON p.id_producto = pr.id_producto 
                    AND pr.fecha >= %s
                GROUP BY p.id_producto, p.nombre
            """, (fecha_limite,))
            produccion_data = {row['id_producto']: {'nombre': row['nombre'], 'produccion': int(row['produccion_total'])} for row in cursor.fetchall()}
            
            # Luego obtenemos las ventas por producto (último mes)
            cursor.execute("""
                SELECT 
                    p.id_producto,
                    p.nombre,
                    COALESCE(SUM(v.cantidad), 0) as ventas_total
                FROM productos p
                LEFT JOIN ventas v ON p.id_producto = v.id_producto 
                    AND v.fecha >= %s
                GROUP BY p.id_producto, p.nombre
            """, (fecha_limite,))
            ventas_data = {row['id_producto']: {'nombre': row['nombre'], 'ventas': int(row['ventas_total'])} for row in cursor.fetchall()}
            
            print(f"📅 Usando datos desde: {fecha_limite}")
            
            # Combinamos los datos
            comparativa_result = []
            all_productos = set(produccion_data.keys()) | set(ventas_data.keys());
            
            for producto_id in all_productos:
                nombre = produccion_data.get(producto_id, {}).get('nombre') or ventas_data.get(producto_id, {}).get('nombre')
                produccion = produccion_data.get(producto_id, {}).get('produccion', 0)
                ventas = ventas_data.get(producto_id, {}).get('ventas', 0)
                
                if produccion > 0 or ventas > 0:  # Solo incluir productos con actividad
                    comparativa_result.append({
                        'nombre': nombre,
                        'produccion': produccion,
                        'ventas': ventas
                    })
            
            # Ordenar por producción y tomar los top 5
            comparativa_result.sort(key=lambda x: x['produccion'], reverse=True)
            comparativa_result = comparativa_result[:5]
            
            comparativa_labels = [row['nombre'] for row in comparativa_result]
            comparativa_produccion = [row['produccion'] for row in comparativa_result]
            comparativa_ventas = [row['ventas'] for row in comparativa_result]
            
            print(f"✅ Comparativa corregida: {len(comparativa_result)} resultados")
            print(f"📋 Comparativa labels: {comparativa_labels}")
            print(f"📋 Producción cantidades: {comparativa_produccion}")
            print(f"📋 Ventas cantidades: {comparativa_ventas}")
        except Exception as e:
            print(f"❌ Error en comparativa: {e}")
            comparativa_labels = []
            comparativa_produccion = []
            comparativa_ventas = []

        # Estadísticas de ventas - CORREGIDAS CON FILTRO DE FECHA
        try:
            print("📈 Ejecutando estadísticas de ventas corregidas...")
            cursor.execute("SELECT COUNT(*) AS total_transacciones FROM ventas WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
            total_ventas = cursor.fetchone()['total_transacciones'] or 0

            cursor.execute("SELECT SUM(total) AS ingresos_totales FROM ventas WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
            ingresos_totales = cursor.fetchone()['ingresos_totales'] or 0

            cursor.execute("SELECT AVG(total) AS promedio_por_venta FROM ventas WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
            promedio_venta = cursor.fetchone()['promedio_por_venta'] or 0
            
            # Obtener el total de unidades vendidas para el ratio (último mes)
            cursor.execute("SELECT SUM(cantidad) AS total_unidades_vendidas FROM ventas WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
            total_unidades_vendidas = cursor.fetchone()['total_unidades_vendidas'] or 0
            
            print(f"✅ Stats (último mes) - Total transacciones: {total_ventas}")
            print(f"✅ Stats (último mes) - Total unidades vendidas: {total_unidades_vendidas}")
            print(f"✅ Stats (último mes) - Ingresos totales: {ingresos_totales}")
        except Exception as e:
            print(f"❌ Error en estadísticas de ventas: {e}")
            total_ventas = 0
            ingresos_totales = 0
            promedio_venta = 0
            total_unidades_vendidas = 0

        # Ratio ventas/producción - CORREGIDO
        if total_produccion > 0:
            # Usar total de unidades vendidas, no suma de valores de ventas
            ratio_ventas_produccion = round((total_unidades_vendidas / total_produccion) * 100, 1)
        else:
            ratio_ventas_produccion = 0
            
        print(f"📊 Ratio calculado: {total_unidades_vendidas} unidades vendidas / {total_produccion} unidades producidas = {ratio_ventas_produccion}%")

        # Top ventas por producto - CON FILTRO DE FECHA
        try:
            cursor.execute("""
                SELECT 
                    p.nombre as producto_nombre,
                    SUM(v.cantidad) as cantidad,
                    SUM(v.total) as ingresos
                FROM ventas v
                JOIN productos p ON v.id_producto = p.id_producto
                WHERE v.fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY p.id_producto, p.nombre
                ORDER BY ingresos DESC
                LIMIT 5
            """)
            top_ventas = cursor.fetchall()
            print(f"✅ Top ventas (último mes): {len(top_ventas)} resultados")
        except Exception as e:
            print(f"Error en top ventas: {e}")
            top_ventas = []

        # Datos para gráfico de producción por responsable
        try:
            cursor.execute("""
                SELECT 
                    CONCAT(r.nombre, ' ', r.apellido) as responsable,
                    SUM(pr.cantidad) as total
                FROM produccion pr
                JOIN produccion_responsable pro_resp ON pr.id_produccion = pro_resp.id_produccion
                JOIN responsables r ON pro_resp.id_responsable = r.id_responsable
                GROUP BY r.id_responsable, r.nombre, r.apellido
                ORDER BY total DESC
                LIMIT 5
            """)
            responsables_data = cursor.fetchall()
            responsables_labels = [row['responsable'] for row in responsables_data]
            responsables_values = [row['total'] for row in responsables_data]
        except:
            responsables_labels = []
            responsables_values = []

        # 🎯 LOG FINAL DE DATOS ANTES DE ENVIAR AL TEMPLATE
        print("=" * 50)
        print("🎯 DATOS FINALES PARA EL TEMPLATE:")
        print(f"Ventas labels: {ventas_labels}")
        print(f"Ventas values: {ventas_values}")
        print(f"Ventas diarias labels: {ventas_diarias_labels}")
        print(f"Ventas diarias values: {ventas_diarias_values}")
        print(f"Ingresos labels: {ingresos_labels}")
        print(f"Ingresos values: {ingresos_values}")
        print(f"Comparativa labels: {comparativa_labels}")
        print(f"Total ventas: {total_ventas}")
        print(f"Ingresos totales: {ingresos_totales}")
        print("=" * 50)

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
            zip=zip,
            ventas_labels=ventas_labels,
            ventas_values=ventas_values,
            ingresos_labels=ingresos_labels,
            ingresos_values=ingresos_values,
            comparativa_labels=comparativa_labels,
            comparativa_produccion=comparativa_produccion,
            comparativa_ventas=comparativa_ventas,
            total_ventas=total_ventas,
            ingresos_totales=ingresos_totales,
            promedio_venta=promedio_venta,
            ratio_ventas_produccion=ratio_ventas_produccion,
            top_ventas=top_ventas,
            responsables_labels=responsables_labels,
            responsables_values=responsables_values,
            ventas_diarias_labels=ventas_diarias_labels,
            ventas_diarias_values=ventas_diarias_values
        )

    except Error as err:
        flash(f'Error al cargar el dashboard: {str(err)}', 'danger')
        return redirect(url_for('index'))
    finally:
        conn.close()

@app.route('/dashboard/filtrar', methods=['GET'])  # Solo GET
def dashboard_filtrar():
    if 'usuario_id' not in session or session.get('rol') != 'administrador':
        flash('Debe iniciar sesión como administrador para acceder al dashboard', 'danger')
        return redirect(url_for('login'))

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        # Obtener fecha actual y primer día del mes
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        primer_dia_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')

        # Obtener filtros desde URL (GET)
        fecha_inicio = request.args.get('fecha_inicio', primer_dia_mes)

        fecha_fin = request.args.get('fecha_fin', fecha_actual)
        producto_id = request.args.get('producto', '0')
        responsable_id = request.args.get('responsable', '0')

        # Obtener listas para los selectores
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = cursor.fetchall()
        cursor.execute("SELECT * FROM responsables ORDER BY nombre, apellido")
        responsables = cursor.fetchall()

        # Datos para estadísticas generales (sin filtrar)
        cursor.execute("SELECT COUNT(*) AS total FROM productos")
        total_productos = cursor.fetchone()['total'] or 0
        cursor.execute("SELECT COUNT(*) AS total FROM responsables")
        total_responsables = cursor.fetchone()['total'] or 0

        # 1. Top de Productos FILTRADOS (CORREGIDO)
        productos_query = """
            SELECT p.nombre, SUM(DISTINCT pr.cantidad) as total
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
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

        # 2. Producción diaria FILTRADA (CORREGIDO)
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
        daily_query += " GROUP BY DATE(pr.fecha), pr.id_produccion ORDER BY dia"

        # Mejor aún, usar subconsulta para evitar duplicados
        daily_query_fixed = """
            SELECT dia, SUM(cantidad) as total FROM (
                SELECT DATE(pr.fecha) as dia, pr.cantidad
                FROM produccion pr
                LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
                WHERE 1=1
        """
        if fecha_inicio:
            daily_query_fixed += " AND pr.fecha >= %s"
        if fecha_fin:
            daily_query_fixed += " AND pr.fecha <= %s"
        if producto_id != '0':
            daily_query_fixed += " AND pr.id_producto = %s"
        if responsable_id != '0':
            daily_query_fixed += " AND prr.id_responsable = %s"
        daily_query_fixed += """
                GROUP BY pr.id_produccion, DATE(pr.fecha)
            ) as subquery
            GROUP BY dia ORDER BY dia
        """

        cursor.execute(daily_query_fixed, daily_params)
        daily_data = cursor.fetchall()
        daily_labels = [row['dia'].strftime('%Y-%m-%d') for row in daily_data]
        daily_values = [row['total'] for row in daily_data]

        # 3. Producción por responsable FILTRADA (CORREGIDO)
        resp_query = """
            SELECT responsable, SUM(cantidad) as total FROM (
                SELECT CONCAT(r.nombre, ' ', r.apellido) as responsable, pr.cantidad
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
        resp_query += """
                GROUP BY pr.id_produccion, responsable
            ) as subquery
            GROUP BY responsable ORDER BY total DESC LIMIT 10
        """

        cursor.execute(resp_query, resp_params)
        resp_data = cursor.fetchall()
        responsables_labels = [row['responsable'] or 'Sin asignar' for row in resp_data]
        responsables_values = [row['total'] for row in resp_data]

        # 4. Total de producción FILTRADO (CORREGIDO)
        total_query = """
            SELECT SUM(cantidad) as total FROM (
                SELECT pr.cantidad
                FROM produccion pr
                LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
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
        total_query += """
                GROUP BY pr.id_produccion
            ) as subquery
        """

        cursor.execute(total_query, total_params)
        total_produccion_filtrada = cursor.fetchone()['total'] or 0

        # 5. Tabla de resultados con paginación
        pagina_actual = int(request.args.get('pagina', 1))
        por_pagina = 10
        offset = (pagina_actual - 1) * por_pagina

        # Consulta principal para la tabla
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

        # Contar total para paginación
        count_query = """
            SELECT COUNT(DISTINCT pr.id_produccion) as total
            FROM produccion pr
            LEFT JOIN produccion_responsable prr ON pr.id_produccion = prr.id_produccion
            WHERE 1=1
        """
        if fecha_inicio:
            count_query += " AND pr.fecha >= %s"
        if fecha_fin:
            count_query += " AND pr.fecha <= %s"
        if producto_id != '0':
            count_query += " AND pr.id_producto = %s"
        if responsable_id != '0':
            count_query += " AND prr.id_responsable = %s"

        cursor.execute(count_query, params)
        total_resultados = cursor.fetchone()['total']
        total_paginas = max(1, (total_resultados + por_pagina - 1) // por_pagina)

        # Ejecutar consulta con paginación
        query += " GROUP BY pr.id_produccion ORDER BY pr.fecha DESC"
        query += f" LIMIT {por_pagina} OFFSET {offset}"
        cursor.execute(query, params)
        producciones = cursor.fetchall()

        # Query string para mantener filtros en paginación
        from urllib.parse import urlencode
        filtros = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'producto': producto_id,
            'responsable': responsable_id
        }
        query_string = urlencode({k: v for k, v in filtros.items() if v and v != '0'})

        mostrar_resultados = True

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

@app.route('/dashboard/comparar', methods=['GET'])
def dashboard_comparar():
    if 'usuario_id' not in session or session.get('rol') != 'administrador':
        flash('Debe iniciar sesión como administrador para acceder al dashboard', 'danger')
        return redirect(url_for('login'))

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        # Obtener períodos de comparación
        periodo1_inicio = request.args.get('periodo1_inicio')
        periodo1_fin = request.args.get('periodo1_fin')
        periodo2_inicio = request.args.get('periodo2_inicio')
        periodo2_fin = request.args.get('periodo2_fin')

        if not all([periodo1_inicio, periodo1_fin, periodo2_inicio, periodo2_fin]):
            flash('Debe completar todos los campos de fecha para la comparación', 'warning')
            return redirect(url_for('index'))

        # PERÍODO 1 - Datos de producción
        cursor.execute("""
            SELECT 
                SUM(cantidad) as total_produccion,
                COUNT(DISTINCT id_producto) as productos_producidos,
                COUNT(DISTINCT DATE(fecha)) as dias_activos,
                AVG(cantidad) as promedio_diario
            FROM produccion 
            WHERE fecha BETWEEN %s AND %s
        """, (periodo1_inicio, periodo1_fin))
        stats_periodo1 = cursor.fetchone()

        # Top productos período 1
        cursor.execute("""
            SELECT p.nombre, SUM(pr.cantidad) as total
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            WHERE pr.fecha BETWEEN %s AND %s
            GROUP BY p.id_producto, p.nombre
            ORDER BY total DESC LIMIT 5
        """, (periodo1_inicio, periodo1_fin))
        top_productos_p1 = cursor.fetchall()

        # PERÍODO 2 - Datos de producción
        cursor.execute("""
            SELECT 
                SUM(cantidad) as total_produccion,
                COUNT(DISTINCT id_producto) as productos_producidos,
                COUNT(DISTINCT DATE(fecha)) as dias_activos,
                AVG(cantidad) as promedio_diario
            FROM produccion 
            WHERE fecha BETWEEN %s AND %s
        """, (periodo2_inicio, periodo2_fin))
        stats_periodo2 = cursor.fetchone()

        # Top productos período 2
        cursor.execute("""
            SELECT p.nombre, SUM(pr.cantidad) as total
            FROM produccion pr
            JOIN productos p ON pr.id_producto = p.id_producto
            WHERE pr.fecha BETWEEN %s AND %s
            GROUP BY p.id_producto, p.nombre
            ORDER BY total DESC LIMIT 5
        """, (periodo2_inicio, periodo2_fin))
        top_productos_p2 = cursor.fetchall()

        # Calcular diferencias y porcentajes
        diferencia_produccion = (stats_periodo2['total_produccion'] or 0) - (stats_periodo1['total_produccion'] or 0)
        porcentaje_cambio = 0
        if stats_periodo1['total_produccion'] and stats_periodo1['total_produccion'] > 0:
            porcentaje_cambio = (diferencia_produccion / stats_periodo1['total_produccion']) * 100

        # Análisis de tendencias (por día)
        cursor.execute("""
            SELECT DATE(fecha) as dia, SUM(cantidad) as total
            FROM produccion 
            WHERE fecha BETWEEN %s AND %s
            GROUP BY DATE(fecha)
            ORDER BY dia
        """, (periodo1_inicio, periodo1_fin))
        tendencia_p1 = cursor.fetchall()

        cursor.execute("""
            SELECT DATE(fecha) as dia, SUM(cantidad) as total
            FROM produccion 
            WHERE fecha BETWEEN %s AND %s
            GROUP BY DATE(fecha)
            ORDER BY dia
        """, (periodo2_inicio, periodo2_fin))
        tendencia_p2 = cursor.fetchall()

        return render_template(
            "dashboard/comparacion.html",
            periodo1_inicio=periodo1_inicio,
            periodo1_fin=periodo1_fin,
            periodo2_inicio=periodo2_inicio,
            periodo2_fin=periodo2_fin,
            stats_periodo1=stats_periodo1,
            stats_periodo2=stats_periodo2,
            top_productos_p1=top_productos_p1,
            top_productos_p2=top_productos_p2,
            diferencia_produccion=diferencia_produccion,
            porcentaje_cambio=porcentaje_cambio,
            tendencia_p1=tendencia_p1,
            tendencia_p2=tendencia_p2
        )

    except Exception as e:
        flash(f'Error al realizar la comparación: {str(e)}', 'danger')
        return redirect(url_for('index'))
    finally:
        conn.close()
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Endpoint para exportar dashboard completo a PDF
@app.route('/export/dashboard/pdf', methods=['POST'])
def export_dashboard_pdf():
    try:
        from flask import jsonify
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, PageBreak, Image
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, Spacer
        import tempfile
        import base64
        from io import BytesIO
        
        data = request.get_json()
        images = data.get('images', {})
        filters = data.get('filters', {})
        
        # Crear un buffer para el PDF
        buffer = BytesIO()
        
        # Crear el documento PDF en orientación horizontal
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        story = []
        
        # Obtener estilos
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['Normal']
        
        # Título
        title = Paragraph("Dashboard Completo - Chocopasión", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Información de filtros
        if filters:
            filters_info = "Filtros aplicados: "
            if filters.get('fecha_inicio'):
                filters_info += f"Desde: {filters.get('fecha_inicio')} "
            if filters.get('fecha_fin'):
                filters_info += f"Hasta: {filters.get('fecha_fin')} "
            if filters.get('producto') and filters.get('producto') != '0':
                filters_info += f"Producto ID: {filters.get('producto')} "
            
            filter_para = Paragraph(filters_info, normal_style)
            story.append(filter_para)
            story.append(Spacer(1, 20))
        
        # Función para agregar imagen al PDF
        def add_image_to_story(img_data, title_text):
            if img_data:
                try:
                    # Decodificar imagen base64
                    img_data = img_data.split(',')[1] if ',' in img_data else img_data
                    img_bytes = base64.b64decode(img_data)
                    
                    # Crear imagen temporal
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        tmp_file.write(img_bytes)
                        tmp_file.flush()
                        
                        # Agregar título de la sección
                        section_title = Paragraph(title_text, styles['Heading2'])
                        story.append(section_title)
                        story.append(Spacer(1, 10))
                        
                        # Agregar imagen al story
                        img = Image(tmp_file.name, width=500, height=250)
                        story.append(img)
                        story.append(Spacer(1, 20))
                        
                    # Limpiar archivo temporal
                    os.unlink(tmp_file.name)
                    
                except Exception as e:
                    print(f"Error procesando imagen {title_text}: {e}")
        
        # Agregar cada gráfico
        add_image_to_story(images.get('productsImg'), "Producción por Producto")
        add_image_to_story(images.get('dailyImg'), "Producción Diaria")
        add_image_to_story(images.get('respImg'), "Producción por Responsable")
        
        
        # Construir el PDF
        doc.build(story)
        

        
        # Obtener el contenido del buffer
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Crear respuesta
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=dashboard_completo.pdf'
        
        return response
        
    except Exception as e:
        print(f"Error al generar PDF: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)