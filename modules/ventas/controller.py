from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .service import VentaService
from datetime import datetime

# Crear blueprint para ventas
ventas_bp = Blueprint('ventas', __name__)

class VentaController:
    def __init__(self):
        self.venta_service = VentaService()

# Instancia del controlador
venta_controller = VentaController()

@ventas_bp.route('/')
def index():
    """Listar todas las ventas"""
    try:
        ventas = venta_controller.venta_service.obtener_ventas()
        return render_template('ventas/index.html', ventas=ventas)
    except Exception as e:
        flash(f'Error al cargar las ventas: {str(e)}', 'danger')
        return render_template('ventas/index.html', ventas=[])

@ventas_bp.route('/agregar')
def agregar():
    """Mostrar formulario para agregar nueva venta"""
    try:
        productos = venta_controller.venta_service.obtener_productos()
        presentaciones = venta_controller.venta_service.obtener_presentaciones()
        return render_template('ventas/agregar.html', productos=productos, presentaciones=presentaciones)
    except Exception as e:
        flash(f'Error al cargar datos: {str(e)}', 'danger')
        return render_template('ventas/agregar.html', productos=[], presentaciones=[])

@ventas_bp.route('/crear', methods=['POST'])
def crear():
    """Crear nueva venta"""
    try:
        fecha = request.form.get('fecha')
        id_producto = request.form.get('id_producto')
        id_presentacion = request.form.get('id_presentacion')
        cantidad = request.form.get('cantidad')
        precio_unitario = request.form.get('precio_unitario')
        
        # Validaciones
        if not all([fecha, id_producto, id_presentacion, cantidad, precio_unitario]):
            flash('Todos los campos son obligatorios', 'warning')
            return redirect(url_for('ventas.agregar'))
        
        # Crear venta
        venta = venta_controller.venta_service.crear_venta(
            fecha=fecha,
            id_producto=int(id_producto),
            id_presentacion=int(id_presentacion),
            cantidad=int(cantidad),
            precio_unitario=float(precio_unitario)
        )
        
        if venta:
            flash('Venta creada exitosamente', 'success')
        else:
            flash('Error al crear la venta', 'danger')
        
        return redirect(url_for('ventas.index'))
        
    except ValueError as e:
        flash('Datos inválidos proporcionados', 'danger')
        return redirect(url_for('ventas.agregar'))
    except Exception as e:
        flash(f'Error al crear la venta: {str(e)}', 'danger')
        return redirect(url_for('ventas.agregar'))

@ventas_bp.route('/ver/<int:id_venta>')
def ver(id_venta):
    """Ver detalles de una venta específica"""
    try:
        venta = venta_controller.venta_service.obtener_venta_por_id(id_venta)
        if not venta:
            flash('Venta no encontrada', 'warning')
            return redirect(url_for('ventas.index'))
        
        return render_template('ventas/ver.html', venta=venta)
        
    except Exception as e:
        flash(f'Error al cargar la venta: {str(e)}', 'danger')
        return redirect(url_for('ventas.index'))

@ventas_bp.route('/eliminar/<int:id_venta>')
def eliminar(id_venta):
    """Eliminar una venta"""
    try:
        if venta_controller.venta_service.eliminar_venta(id_venta):
            flash('Venta eliminada exitosamente', 'success')
        else:
            flash('No se pudo eliminar la venta', 'warning')
        return redirect(url_for('ventas.index'))
        
    except Exception as e:
        flash(f'Error al eliminar la venta: {str(e)}', 'danger')
        return redirect(url_for('ventas.index'))

@ventas_bp.route('/buscar')
def buscar():
    """Buscar ventas por fecha"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        ventas = []
        
        if fecha_inicio and fecha_fin:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            ventas = venta_controller.venta_service.buscar_ventas_por_fecha(fecha_inicio, fecha_fin)
        else:
            ventas = venta_controller.venta_service.obtener_ventas()
        
        return render_template('ventas/index.html', ventas=ventas)
        
    except Exception as e:
        flash(f'Error en la búsqueda: {str(e)}', 'danger')
        return redirect(url_for('ventas.index'))

# API endpoints
@ventas_bp.route('/api/precio-vigente')
def api_precio_vigente():
    """API para obtener precio vigente de un producto y presentación"""
    try:
        id_producto = request.args.get('id_producto', type=int)
        id_presentacion = request.args.get('id_presentacion', type=int)
        fecha = request.args.get('fecha')
        
        if not id_producto or not id_presentacion:
            return jsonify({'error': 'Producto y presentación son requeridos'}), 400
        
        fecha_consulta = None
        if fecha:
            fecha_consulta = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        precio = venta_controller.venta_service.obtener_precio_vigente(
            id_producto, id_presentacion, fecha_consulta
        )
        
        if precio is not None:
            return jsonify({'precio': float(precio)})
        else:
            return jsonify({'error': 'No hay precio vigente para esta combinación'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
