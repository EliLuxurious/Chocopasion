#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos y verificar los datos de precios

Conexión: usa variables de entorno del .env
  - Docker:  host=127.0.0.1, port=3307, user=chocouser, password=chocopassword
  - Laragon: host=127.0.0.1, port=3306, user=root, password=''
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def _get_conn_params():
    host = os.getenv('MYSQL_HOST', '127.0.0.1')
    if host == 'db':          # nombre de servicio Docker → no resolvible desde el host
        host = '127.0.0.1'
    return {
        'host':     host,
        'port':     int(os.getenv('MYSQL_PORT', 3307)),
        'user':     os.getenv('MYSQL_USER', 'chocouser'),
        'password': os.getenv('MYSQL_PASSWORD', 'chocopassword'),
        'database': os.getenv('MYSQL_DATABASE', 'chocopasion2'),
        'charset':  'utf8mb4',
    }

def test_database_connection():
    """Probar conexión y mostrar datos de precios"""
    params = _get_conn_params()
    print(f"🔌 Conectando a {params['host']}:{params['port']} / {params['database']}...")
    connection = None
    try:
        # Conectar a la base de datos chocopasion2
        connection = mysql.connector.connect(**params)
        
        if connection.is_connected():
            print("✅ Conexión exitosa a chocopasion2")
            
            cursor = connection.cursor(dictionary=True)
            
            # Verificar que existan las tablas
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\n📋 Tablas encontradas: {len(tables)}")
            for table in tables:
                print(f"   - {list(table.values())[0]}")
            
            # Verificar datos en tabla precios
            cursor.execute("SELECT COUNT(*) as total FROM precios")
            count_result = cursor.fetchone()
            print(f"\n💰 Total de registros en tabla precios: {count_result['total']}")
            
            # Mostrar algunos precios con información de productos y presentaciones
            query = """
                SELECT p.id_precio, p.precio_unitario,
                       pr.nombre as producto_nombre,
                       pe.descripcion as presentacion_descripcion
                FROM precios p
                INNER JOIN productos pr ON p.id_producto = pr.id_producto
                INNER JOIN presentaciones pe ON p.id_presentacion = pe.id_presentacion
                LIMIT 10
            """
            cursor.execute(query)
            precios = cursor.fetchall()
            
            print(f"\n📋 Primeros 10 precios:")
            for precio in precios:
                print(f"   ID: {precio['id_precio']} | Producto: {precio['producto_nombre']} | Presentación: {precio['presentacion_descripcion']} | Precio: ${precio['precio_unitario']}")
            
            # Verificar datos en tabla productos
            cursor.execute("SELECT COUNT(*) as total FROM productos")
            count_result = cursor.fetchone()
            print(f"\n🍫 Total de productos: {count_result['total']}")
            
            # Verificar datos en tabla presentaciones
            cursor.execute("SELECT COUNT(*) as total FROM presentaciones")
            count_result = cursor.fetchone()
            print(f"\n📦 Total de presentaciones: {count_result['total']}")
            
            return True
            
    except Error as err:
        print(f"❌ Error de conexión: {err}")
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔐 Conexión cerrada")

if __name__ == "__main__":
    print("🔍 Probando conexión a base de datos...")
    test_database_connection()
