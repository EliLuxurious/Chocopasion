#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para cargar ventas desde Excel a la base de datos
Archivo: ventas_simuladas_corregidas.xlsx
Columnas: fecha, producto, presentacion, cantidad, precio_unitario
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

def conectar():
    """Conectar a la base de datos MySQL"""
    try:
        print("🔌 Conectando a la base de datos...")
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='chocopasion2',
            port=3306,
            auth_plugin='mysql_native_password'
        )
        print("✅ Conexión exitosa a la base de datos")
        return conn
    except Error as err:
        print(f"❌ Error al conectar a la base de datos: {err}")
        raise

def obtener_productos(cursor):
    """Obtener diccionario de productos: nombre -> id"""
    cursor.execute("SELECT id_producto, nombre FROM productos")
    productos = cursor.fetchall()
    return {nombre.strip().lower(): id_producto for id_producto, nombre in productos}

def obtener_presentaciones(cursor):
    """Obtener diccionario de presentaciones: descripcion -> id"""
    cursor.execute("SELECT id_presentacion, descripcion FROM presentaciones")
    presentaciones = cursor.fetchall()
    return {desc.strip().lower(): id_presentacion for id_presentacion, desc in presentaciones}

def cargar_ventas_desde_excel():
    """Función principal para cargar ventas desde Excel"""
    archivo_excel = "ventas_simuladas_corregidas.xlsx"
    
    if not os.path.exists(archivo_excel):
        print(f"❌ Error: No se encontró el archivo {archivo_excel}")
        return

    try:
        print(f"📖 Leyendo archivo: {archivo_excel}")
        df = pd.read_excel(archivo_excel)
        print(f"📊 Datos leídos: {len(df)} filas")
        print(f"📋 Columnas encontradas: {list(df.columns)}\n")

        conn = conectar()
        cursor = conn.cursor()

        productos_dict = obtener_productos(cursor)
        presentaciones_dict = obtener_presentaciones(cursor)

        insertados = 0
        errores = 0
        productos_no_encontrados = set()
        presentaciones_no_encontradas = set()

        print(f"🚀 Iniciando carga de {len(df)} registros...\n")

        for index, row in df.iterrows():
            try:
                fecha = row['fecha']
                producto_nombre = str(row['producto']).strip().lower()
                presentacion_desc = str(row['presentacion']).strip().lower()
                cantidad = int(row['cantidad'])
                precio_unitario = float(row['precio_unitario'])

                # Convertir fecha
                if isinstance(fecha, str):
                    fecha_obj = pd.to_datetime(fecha).date()
                else:
                    fecha_obj = fecha.date() if hasattr(fecha, 'date') else fecha

                id_producto = productos_dict.get(producto_nombre)
                if not id_producto:
                    productos_no_encontrados.add(producto_nombre)
                    errores += 1
                    continue

                id_presentacion = presentaciones_dict.get(presentacion_desc)
                if not id_presentacion:
                    presentaciones_no_encontradas.add(presentacion_desc)
                    errores += 1
                    continue

                cursor.execute("""
                    INSERT INTO ventas (fecha, id_producto, id_presentacion, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s, %s)
                """, (fecha_obj, id_producto, id_presentacion, cantidad, precio_unitario))

                insertados += 1

                if insertados % 50 == 0:
                    print(f"📈 Procesados: {insertados} registros...")

            except Exception as e:
                print(f"❌ Error en fila {index + 2}: {str(e)}")
                errores += 1
                continue

        conn.commit()

        print(f"\n🎉 PROCESO COMPLETADO:")
        print(f"✅ Registros insertados: {insertados}")
        print(f"❌ Errores: {errores}")
        print(f"📊 Total procesado: {insertados + errores}")

        if productos_no_encontrados:
            print("\n⚠️ Productos no encontrados en la BD:")
            for p in sorted(productos_no_encontrados):
                print(f" - {p}")

        if presentaciones_no_encontradas:
            print("\n⚠️ Presentaciones no encontradas en la BD:")
            for p in sorted(presentaciones_no_encontradas):
                print(f" - {p}")

        cursor.execute("""
            SELECT COUNT(*) as total,
                   DATE(MIN(fecha)) as fecha_min,
                   DATE(MAX(fecha)) as fecha_max
            FROM ventas
        """)
        resultado = cursor.fetchone()
        print(f"\n📈 ESTADO ACTUAL DE VENTAS:")
        print(f"📊 Total registros en BD: {resultado[0]}")
        print(f"📅 Fecha más antigua: {resultado[1]}")
        print(f"📅 Fecha más reciente: {resultado[2]}")

    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        if 'conn' in locals():
            conn.rollback()

    finally:
        if 'conn' in locals():
            conn.close()
            print("🔌 Conexión cerrada")

if __name__ == "__main__":
    print("🚀 INICIANDO CARGA DE VENTAS DESDE EXCEL")
    print("=" * 50)
    cargar_ventas_desde_excel()
    print("=" * 50)
    print("✅ PROCESO FINALIZADO")
