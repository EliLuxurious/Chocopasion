import mysql.connector
from mysql.connector import Error

class ProductoRepository:
    @staticmethod
    def conectar():
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                password='',
                database='chocopasion',
                port=3306
            )
            return conn
        except Error as err:
            print(f"Error de conexión: {err}")
            raise

    @staticmethod
    def get_all():
        conn = ProductoRepository.conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
        return productos
    
    @staticmethod
    def get_by_id(id):
        conn = ProductoRepository.conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
        producto = cursor.fetchone()
        cursor.close()
        conn.close()
        return producto
    
    @staticmethod
    def get_by_codigo(codigo):
        conn = ProductoRepository.conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE codigo = %s", (codigo,))
        producto = cursor.fetchone()
        cursor.close()
        conn.close()
        return producto
    
    @staticmethod
    def create(producto_data):
        conn = ProductoRepository.conectar()
        cursor = conn.cursor()
        sql = """
            INSERT INTO productos (codigo, nombre, descripcion, precio, unidad)
            VALUES (%s, %s, %s, %s, %s)
        """
        valores = (
            producto_data['codigo'],
            producto_data['nombre'],
            producto_data.get('descripcion'),
            producto_data['precio'],
            producto_data['unidad']
        )
        cursor.execute(sql, valores)
        conn.commit()
        id = cursor.lastrowid
        cursor.close()
        conn.close()
        return id
    
    @staticmethod
    def update(id, producto_data):
        conn = ProductoRepository.conectar()
        cursor = conn.cursor()
        sql = """
            UPDATE productos 
            SET codigo = %s, nombre = %s, descripcion = %s, precio = %s, unidad = %s
            WHERE id = %s
        """
        valores = (
            producto_data['codigo'],
            producto_data['nombre'],
            producto_data.get('descripcion'),
            producto_data['precio'],
            producto_data['unidad'],
            id
        )
        cursor.execute(sql, valores)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    
    @staticmethod
    def delete(id):
        conn = ProductoRepository.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
