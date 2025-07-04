import mysql.connector
from mysql.connector import Error

def get_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='chocopasion1',
            charset='utf8mb4'
        )
        return connection
    except Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

class ProductoService:
    def obtener_productos(self):
        """Obtener todos los productos"""
        connection = get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id_producto as id, nombre FROM productos ORDER BY nombre"
            cursor.execute(query)
            productos = cursor.fetchall()
            return productos
            
        except Error as err:
            print(f"Error al obtener productos: {err}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def obtener_producto_por_id(self, id_producto):
        """Obtener un producto por su ID"""
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id_producto as id, nombre FROM productos WHERE id_producto = %s"
            cursor.execute(query, (id_producto,))
            producto = cursor.fetchone()
            return producto
            
        except Error as err:
            print(f"Error al obtener producto: {err}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
