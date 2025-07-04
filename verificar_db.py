import mysql.connector
from mysql.connector import Error

def verificar_db():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='chocopasion2',
            port=3306,
            auth_plugin='mysql_native_password'
        )
        
        cursor = connection.cursor()
        
        # Verificar qué tablas existen
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        print("Tablas en chocopasion2:")
        for tabla in tablas:
            print(f"- {tabla[0]}")
        
        # Verificar si existe la tabla precios
        cursor.execute("SHOW TABLES LIKE 'precios'")
        tabla_precios = cursor.fetchone()
        
        if tabla_precios:
            print("\n✅ Tabla precios existe")
            cursor.execute("DESCRIBE precios")
            columnas = cursor.fetchall()
            print("Estructura de la tabla precios:")
            for columna in columnas:
                print(f"  {columna[0]} - {columna[1]}")
                
            # Verificar datos en precios
            cursor.execute("SELECT COUNT(*) FROM precios")
            count = cursor.fetchone()[0]
            print(f"\nCantidad de registros en precios: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM precios LIMIT 3")
                datos = cursor.fetchall()
                print("Primeros 3 registros:")
                for dato in datos:
                    print(f"  {dato}")
        else:
            print("\n❌ Tabla precios NO existe")
        
        # Verificar si existe la tabla presentaciones
        cursor.execute("SHOW TABLES LIKE 'presentaciones'")
        tabla_presentaciones = cursor.fetchone()
        
        if tabla_presentaciones:
            print("\n✅ Tabla presentaciones existe")
            cursor.execute("SELECT COUNT(*) FROM presentaciones")
            count = cursor.fetchone()[0]
            print(f"Cantidad de registros en presentaciones: {count}")
        else:
            print("\n❌ Tabla presentaciones NO existe")
            
        # Verificar tabla productos
        cursor.execute("SHOW TABLES LIKE 'productos'")
        tabla_productos = cursor.fetchone()
        
        if tabla_productos:
            print("\n✅ Tabla productos existe")
            cursor.execute("SELECT COUNT(*) FROM productos")
            count = cursor.fetchone()[0]
            print(f"Cantidad de registros en productos: {count}")
        else:
            print("\n❌ Tabla productos NO existe")
        
        connection.close()
        
    except Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    verificar_db()
