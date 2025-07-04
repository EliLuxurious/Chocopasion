import mysql.connector
from mysql.connector import Error
from .model import Precio

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

class PrecioRepository:
    def obtener_todos(self):
        """Obtener todos los precios con información de productos y presentaciones"""
        print("DEBUG: Intentando conectar a la base de datos...")
        connection = get_connection()
        if not connection:
            print("DEBUG ERROR: No se pudo establecer conexión a la base de datos")
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Primero verificar si las tablas existen
            cursor.execute("SHOW TABLES LIKE 'precios'")
            tabla_precios = cursor.fetchone()
            print(f"DEBUG: Tabla precios existe: {tabla_precios is not None}")
            
            cursor.execute("SHOW TABLES LIKE 'productos'")
            tabla_productos = cursor.fetchone()
            print(f"DEBUG: Tabla productos existe: {tabla_productos is not None}")
            
            cursor.execute("SHOW TABLES LIKE 'presentaciones'")
            tabla_presentaciones = cursor.fetchone()
            print(f"DEBUG: Tabla presentaciones existe: {tabla_presentaciones is not None}")
            
            if not (tabla_precios and tabla_productos and tabla_presentaciones):
                print("DEBUG ERROR: Una o más tablas necesarias no existen")
                return []
            
            query = """
                SELECT p.id_precio, p.id_producto, p.id_presentacion, 
                       p.precio_unitario,
                       pr.nombre as producto_nombre,
                       pe.descripcion as presentacion_nombre
                FROM precios p
                INNER JOIN productos pr ON p.id_producto = pr.id_producto
                INNER JOIN presentaciones pe ON p.id_presentacion = pe.id_presentacion
                ORDER BY pr.nombre, pe.descripcion
            """
            print(f"DEBUG: Ejecutando query: {query}")
            cursor.execute(query)
            precios_data = cursor.fetchall()
            print(f"DEBUG: Query ejecutada, {len(precios_data)} registros encontrados")
            
            precios = []
            for precio_data in precios_data:
                precio = Precio(
                    id_precio=precio_data['id_precio'],
                    id_producto=precio_data['id_producto'],
                    id_presentacion=precio_data['id_presentacion'],
                    precio_unitario=precio_data['precio_unitario'],
                    producto_nombre=precio_data['producto_nombre'],
                    presentacion_nombre=precio_data['presentacion_nombre']
                )
                precios.append(precio)
            
            print(f"DEBUG: Se crearon {len(precios)} objetos Precio")
            return precios
            
        except Error as err:
            print(f"DEBUG ERROR SQL: {err}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("DEBUG: Conexión cerrada")

    def obtener_por_id(self, id_precio):
        """Obtener un precio por su ID"""
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT p.id_precio, p.id_producto, p.id_presentacion, 
                       p.precio_unitario,
                       pr.nombre as producto_nombre,
                       pe.descripcion as presentacion_nombre
                FROM precios p
                INNER JOIN productos pr ON p.id_producto = pr.id_producto
                INNER JOIN presentaciones pe ON p.id_presentacion = pe.id_presentacion
                WHERE p.id_precio = %s
            """
            cursor.execute(query, (id_precio,))
            precio_data = cursor.fetchone()
            
            if precio_data:
                return Precio(
                    id_precio=precio_data['id_precio'],
                    id_producto=precio_data['id_producto'],
                    id_presentacion=precio_data['id_presentacion'],
                    precio_unitario=precio_data['precio_unitario'],
                    producto_nombre=precio_data['producto_nombre'],
                    presentacion_nombre=precio_data['presentacion_nombre']
                )
            return None
            
        except Error as err:
            print(f"Error al obtener precio: {err}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def agregar(self, precio):
        """Agregar un nuevo precio"""
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO precios (id_producto, id_presentacion, precio_unitario)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (
                precio.id_producto,
                precio.id_presentacion,
                precio.precio_unitario
            ))
            connection.commit()
            
            precio.id_precio = cursor.lastrowid
            return precio
            
        except Error as err:
            print(f"Error al agregar precio: {err}")
            connection.rollback()
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def actualizar(self, precio):
        """Actualizar un precio existente"""
        connection = get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            query = """
                UPDATE precios 
                SET id_producto = %s, id_presentacion = %s, precio_unitario = %s
                WHERE id_precio = %s
            """
            cursor.execute(query, (
                precio.id_producto,
                precio.id_presentacion,
                precio.precio_unitario,
                precio.id_precio
            ))
            connection.commit()
            return cursor.rowcount > 0
            
        except Error as err:
            print(f"Error al actualizar precio: {err}")
            connection.rollback()
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def eliminar(self, id_precio):
        """Eliminar un precio"""
        connection = get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM precios WHERE id_precio = %s", (id_precio,))
            connection.commit()
            return cursor.rowcount > 0
            
        except Error as err:
            print(f"Error al eliminar precio: {err}")
            connection.rollback()
            return False
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

    def obtener_precio_actual(self, id_producto, id_presentacion):
        """Obtener el precio actual para un producto y presentación"""
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT precio_unitario
                FROM precios 
                WHERE id_producto = %s AND id_presentacion = %s
                LIMIT 1
            """
            cursor.execute(query, (id_producto, id_presentacion))
            result = cursor.fetchone()
            
            return result['precio_unitario'] if result else None
            
        except Error as err:
            print(f"Error al obtener precio actual: {err}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def obtener_presentaciones_con_precio(self, id_producto):
        """Obtener presentaciones que tienen precio configurado para un producto específico"""
        connection = get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT DISTINCT pe.id_presentacion, pe.descripcion as nombre
                FROM precios p
                INNER JOIN presentaciones pe ON p.id_presentacion = pe.id_presentacion
                WHERE p.id_producto = %s
                ORDER BY pe.descripcion
            """
            cursor.execute(query, (id_producto,))
            return cursor.fetchall()
            
        except Error as err:
            print(f"Error al obtener presentaciones con precio: {err}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
