import mysql.connector
from mysql.connector import Error
from .model import Venta
from datetime import datetime

def get_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='chocopasion2',
            port=3306,
            auth_plugin='mysql_native_password',
            charset='utf8mb4'
        )
        return connection
    except Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

class VentaRepository:
    def obtener_todas(self):
        """Obtener todas las ventas"""
        connection = get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT v.id_venta, v.fecha, v.id_producto, v.id_presentacion, 
                       v.cantidad, v.precio_unitario, v.total,
                       p.nombre as producto_nombre,
                       pr.descripcion as presentacion_nombre
                FROM ventas v
                INNER JOIN productos p ON v.id_producto = p.id_producto
                INNER JOIN presentaciones pr ON v.id_presentacion = pr.id_presentacion
                ORDER BY v.fecha DESC, v.id_venta DESC
            """
            cursor.execute(query)
            ventas_data = cursor.fetchall()
            
            ventas = []
            for venta_data in ventas_data:
                venta = Venta(
                    id_venta=venta_data['id_venta'],
                    fecha=venta_data['fecha'],
                    id_producto=venta_data['id_producto'],
                    id_presentacion=venta_data['id_presentacion'],
                    cantidad=venta_data['cantidad'],
                    precio_unitario=venta_data['precio_unitario'],
                    total=venta_data['total'],
                    producto_nombre=venta_data['producto_nombre'],
                    presentacion_nombre=venta_data['presentacion_nombre']
                )
                ventas.append(venta)
            
            return ventas
            
        except Error as err:
            print(f"Error al obtener ventas: {err}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def obtener_por_id(self, id_venta):
        """Obtener una venta por su ID"""
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT v.id_venta, v.fecha, v.id_producto, v.id_presentacion, 
                       v.cantidad, v.precio_unitario, v.total,
                       p.nombre as producto_nombre,
                       pr.descripcion as presentacion_nombre
                FROM ventas v
                INNER JOIN productos p ON v.id_producto = p.id_producto
                INNER JOIN presentaciones pr ON v.id_presentacion = pr.id_presentacion
                WHERE v.id_venta = %s
            """
            cursor.execute(query, (id_venta,))
            venta_data = cursor.fetchone()
            
            if venta_data:
                return Venta(
                    id_venta=venta_data['id_venta'],
                    fecha=venta_data['fecha'],
                    id_producto=venta_data['id_producto'],
                    id_presentacion=venta_data['id_presentacion'],
                    cantidad=venta_data['cantidad'],
                    precio_unitario=venta_data['precio_unitario'],
                    total=venta_data['total'],
                    producto_nombre=venta_data['producto_nombre'],
                    presentacion_nombre=venta_data['presentacion_nombre']
                )
            return None
            
        except Error as err:
            print(f"Error al obtener venta: {err}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def agregar(self, venta):
        """Agregar una nueva venta"""
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO ventas (fecha, id_producto, id_presentacion, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                venta.fecha,
                venta.id_producto,
                venta.id_presentacion,
                venta.cantidad,
                venta.precio_unitario
            ))
            connection.commit()
            
            # Obtener el ID de la venta recién insertada
            venta.id_venta = cursor.lastrowid
            # El total se calcula automáticamente en la base de datos
            venta.total = venta.cantidad * venta.precio_unitario
            return venta
            
        except Error as err:
            print(f"Error al agregar venta: {err}")
            connection.rollback()
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def eliminar(self, id_venta):
        """Eliminar una venta"""
        connection = get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM ventas WHERE id_venta = %s", (id_venta,))
            connection.commit()
            return cursor.rowcount > 0
            
        except Error as err:
            print(f"Error al eliminar venta: {err}")
            connection.rollback()
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def obtener_ventas_por_fecha(self, fecha_inicio, fecha_fin):
        """Obtener ventas por rango de fechas"""
        connection = get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT v.id_venta, v.fecha, v.id_producto, v.id_presentacion, 
                       v.cantidad, v.precio_unitario, v.total,
                       p.nombre as producto_nombre,
                       pr.nombre as presentacion_nombre
                FROM ventas v
                INNER JOIN productos p ON v.id_producto = p.id_producto
                INNER JOIN presentaciones pr ON v.id_presentacion = pr.id_presentacion
                WHERE v.fecha BETWEEN %s AND %s
                ORDER BY v.fecha DESC, v.id_venta DESC
            """
            cursor.execute(query, (fecha_inicio.date(), fecha_fin.date()))
            ventas_data = cursor.fetchall()
            
            ventas = []
            for venta_data in ventas_data:
                venta = Venta(
                    id_venta=venta_data['id_venta'],
                    fecha=venta_data['fecha'],
                    id_producto=venta_data['id_producto'],
                    id_presentacion=venta_data['id_presentacion'],
                    cantidad=venta_data['cantidad'],
                    precio_unitario=venta_data['precio_unitario'],
                    total=venta_data['total'],
                    producto_nombre=venta_data['producto_nombre'],
                    presentacion_nombre=venta_data['presentacion_nombre']
                )
                ventas.append(venta)
            
            return ventas
            
        except Error as err:
            print(f"Error al obtener ventas por fecha: {err}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def obtener_productos(self):
        """Obtener lista de productos"""
        connection = get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id_producto, nombre FROM productos ORDER BY nombre"
            cursor.execute(query)
            return cursor.fetchall()
            
        except Error as err:
            print(f"Error al obtener productos: {err}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def obtener_presentaciones(self):
        """Obtener lista de presentaciones"""
        connection = get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id_presentacion, descripcion as nombre FROM presentaciones ORDER BY descripcion"
            cursor.execute(query)
            return cursor.fetchall()
            
        except Error as err:
            print(f"Error al obtener presentaciones: {err}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def obtener_precio_vigente(self, id_producto, id_presentacion, fecha=None):
        """Obtener el precio vigente para un producto y presentación"""
        if fecha is None:
            fecha = datetime.now().date()
        
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT precio_unitario
                FROM precios 
                WHERE id_producto = %s AND id_presentacion = %s
                AND fecha_inicio <= %s 
                AND (fecha_fin IS NULL OR fecha_fin >= %s)
                ORDER BY fecha_inicio DESC
                LIMIT 1
            """
            cursor.execute(query, (id_producto, id_presentacion, fecha, fecha))
            result = cursor.fetchone()
            
            return result['precio_unitario'] if result else None
            
        except Error as err:
            print(f"Error al obtener precio vigente: {err}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
