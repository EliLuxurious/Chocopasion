from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .service import PrecioService

# Crear blueprint para precios
precios_bp = Blueprint('precios', __name__)

class PrecioController:
    def __init__(self):
        self.precio_service = PrecioService()

# Instancia del controlador
precio_controller = PrecioController()

@precios_bp.route('/')
def index():
    """Listar todos los precios"""
    try:
        print("DEBUG: Intentando obtener precios...")
        precios = precio_controller.precio_service.obtener_precios()
        print(f"DEBUG: Se obtuvieron {len(precios)} precios")
        
        # Debug: imprimir algunos datos
        for i, precio in enumerate(precios[:3]):  # Solo los primeros 3
            print(f"DEBUG Precio {i}: ID={precio.id_precio}, Producto={precio.producto_nombre}, Precio=${precio.precio_unitario}")
        
        return render_template('precios/index.html', precios=precios)
    except Exception as e:
        print(f"DEBUG ERROR en precios index: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error al cargar los precios: {str(e)}', 'danger')
        return render_template('precios/index.html', precios=[])

@precios_bp.route('/agregar')
def agregar():
    """Mostrar formulario para agregar nuevo precio"""
    try:
        productos = precio_controller.precio_service.obtener_productos()
        presentaciones = precio_controller.precio_service.obtener_presentaciones()
        return render_template('precios/agregar.html', productos=productos, presentaciones=presentaciones)
    except Exception as e:
        flash(f'Error al cargar datos: {str(e)}', 'danger')
        return render_template('precios/agregar.html', productos=[], presentaciones=[])

@precios_bp.route('/crear', methods=['POST'])
def crear():
    """Crear nuevo precio"""
    try:
        id_producto = request.form.get('id_producto')
        id_presentacion = request.form.get('id_presentacion')
        precio_unitario = request.form.get('precio_unitario')
        
        # Validaciones
        if not all([id_producto, id_presentacion, precio_unitario]):
            flash('Todos los campos obligatorios deben ser completados', 'warning')
            return redirect(url_for('precios.agregar'))
        
        # Crear precio
        precio = precio_controller.precio_service.crear_precio(
            id_producto=int(id_producto),
            id_presentacion=int(id_presentacion),
            precio_unitario=float(precio_unitario)
        )
        
        if precio:
            flash('Precio creado exitosamente', 'success')
        else:
            flash('Error al crear el precio', 'danger')
        
        return redirect(url_for('precios.index'))
        
    except ValueError as e:
        flash('Datos inválidos proporcionados', 'danger')
        return redirect(url_for('precios.agregar'))
    except Exception as e:
        flash(f'Error al crear el precio: {str(e)}', 'danger')
        return redirect(url_for('precios.agregar'))

@precios_bp.route('/editar/<int:id_precio>')
def editar(id_precio):
    """Mostrar formulario para editar precio"""
    try:
        precio = precio_controller.precio_service.obtener_precio_por_id(id_precio)
        if not precio:
            flash('Precio no encontrado', 'warning')
            return redirect(url_for('precios.index'))
        
        productos = precio_controller.precio_service.obtener_productos()
        presentaciones = precio_controller.precio_service.obtener_presentaciones()
        
        return render_template('precios/editar.html', precio=precio, productos=productos, presentaciones=presentaciones)
    except Exception as e:
        flash(f'Error al cargar el precio: {str(e)}', 'danger')
        return redirect(url_for('precios.index'))

@precios_bp.route('/actualizar/<int:id_precio>', methods=['POST'])
def actualizar(id_precio):
    """Actualizar precio existente"""
    try:
        id_producto = request.form.get('id_producto')
        id_presentacion = request.form.get('id_presentacion')
        precio_unitario = request.form.get('precio_unitario')
        
        # Validaciones
        if not all([id_producto, id_presentacion, precio_unitario]):
            flash('Todos los campos obligatorios deben ser completados', 'warning')
            return redirect(url_for('precios.editar', id_precio=id_precio))
        
        # Actualizar precio
        exito = precio_controller.precio_service.actualizar_precio(
            id_precio=id_precio,
            id_producto=int(id_producto),
            id_presentacion=int(id_presentacion),
            precio_unitario=float(precio_unitario)
        )
        
        if exito:
            flash('Precio actualizado exitosamente', 'success')
        else:
            flash('Error al actualizar el precio', 'danger')
        
        return redirect(url_for('precios.index'))
        
    except ValueError as e:
        flash('Datos inválidos proporcionados', 'danger')
        return redirect(url_for('precios.editar', id_precio=id_precio))
    except Exception as e:
        flash(f'Error al actualizar el precio: {str(e)}', 'danger')
        return redirect(url_for('precios.editar', id_precio=id_precio))

@precios_bp.route('/eliminar/<int:id_precio>')
def eliminar(id_precio):
    """Eliminar un precio"""
    try:
        if precio_controller.precio_service.eliminar_precio(id_precio):
            flash('Precio eliminado exitosamente', 'success')
        else:
            flash('No se pudo eliminar el precio', 'warning')
        return redirect(url_for('precios.index'))
        
    except Exception as e:
        flash(f'Error al eliminar el precio: {str(e)}', 'danger')
        return redirect(url_for('precios.index'))

# API endpoints
@precios_bp.route('/api/precio-actual')
def api_precio_actual():
    """API para obtener precio actual de un producto y presentación"""
    try:
        id_producto = request.args.get('id_producto', type=int)
        id_presentacion = request.args.get('id_presentacion', type=int)
        
        if not id_producto or not id_presentacion:
            return jsonify({'error': 'Producto y presentación son requeridos'}), 400
        
        precio = precio_controller.precio_service.obtener_precio_actual(
            id_producto, id_presentacion
        )
        
        if precio is not None:
            return jsonify({'precio': float(precio)})
        else:
            return jsonify({'error': 'No hay precio definido para esta combinación'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@precios_bp.route('/api/presentaciones/<int:id_producto>')
def api_presentaciones_producto(id_producto):
    """API para obtener presentaciones disponibles para un producto"""
    try:
        # Esta función requeriría una consulta específica para obtener solo
        # las presentaciones que tienen precios para un producto específico
        presentaciones = precio_controller.precio_service.obtener_presentaciones()
        return jsonify(presentaciones)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@precios_bp.route('/api/presentaciones-producto/<int:id_producto>')
def api_presentaciones_por_producto(id_producto):
    """API para obtener presentaciones que tienen precio configurado para un producto específico"""
    try:
        presentaciones = precio_controller.precio_service.obtener_presentaciones_con_precio(id_producto)
        return jsonify(presentaciones)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
