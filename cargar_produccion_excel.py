#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de carga de datos de PRODUCCIÓN desde Excel a la BD Chocopasión.

Archivos fuente:
  - chocopasion.xlsx   → Hoja1  (datos 2023 — 1484 filas)
  - chocopasion1.xlsx  → Sheet1 (datos 2024 — 1000 filas)

Columnas esperadas en cada Excel:
  FECHA | PRODUCTO | PRESENTACION | CANTIDAD | RESPONSABLE

Notas:
  - RESPONSABLE puede ser un nombre o varios separados por coma.
  - Nombre de responsable = "NOMBRE APELLIDO" (ej: "ELIA SILVA", "JACKELIN AGUIRRE,GELEN MANYA").
  - Se busca coincidencia en la tabla `responsables` por nombre + apellido.
  - La conexión se lee del .env (puerto 3307 para Docker, 3306 para Laragon).

Uso:
    py cargar_produccion_excel.py
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# ── Configuración ──────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

ARCHIVOS = [
    {'path': 'chocopasion.xlsx',  'sheet': 'Hoja1',  'label': 'chocopasion.xlsx (2023)'},
    {'path': 'chocopasion1.xlsx', 'sheet': 'Sheet1', 'label': 'chocopasion1.xlsx (2024)'},
]

# ── Conexión ───────────────────────────────────────────────────────────────────
def conectar():
    host     = os.getenv('MYSQL_HOST', '127.0.0.1')
    if host == 'db':          # servicio Docker → usar 127.0.0.1 desde el host
        host = '127.0.0.1'
    port     = int(os.getenv('MYSQL_PORT', 3307))
    user     = os.getenv('MYSQL_USER', 'chocouser')
    password = os.getenv('MYSQL_PASSWORD', 'chocopassword')
    database = os.getenv('MYSQL_DATABASE', 'chocopasion2')

    print(f"🔌 Conectando a {host}:{port} / {database} como '{user}'...")
    conn = mysql.connector.connect(
        host=host, port=port, user=user, password=password,
        database=database, auth_plugin='mysql_native_password'
    )
    print("✅ Conexión exitosa\n")
    return conn


# ── Carga de catálogos ─────────────────────────────────────────────────────────
def cargar_catalogo_productos(cursor):
    cursor.execute("SELECT id_producto, nombre FROM productos")
    return {nombre.strip().upper(): id_p for id_p, nombre in cursor.fetchall()}

def cargar_catalogo_presentaciones(cursor):
    cursor.execute("SELECT id_presentacion, descripcion FROM presentaciones")
    return {desc.strip().upper(): id_pr for id_pr, desc in cursor.fetchall()}

def cargar_catalogo_responsables(cursor):
    """Devuelve un dict: 'NOMBRE APELLIDO' -> id_responsable"""
    cursor.execute("SELECT id_responsable, nombre, apellido FROM responsables")
    return {
        f"{nom.strip().upper()} {ape.strip().upper()}": id_r
        for id_r, nom, ape in cursor.fetchall()
    }


# ── Parseo de responsables ─────────────────────────────────────────────────────
def parsear_responsables(valor_celda, catalogo, fila_idx):
    """
    Parsea una celda de responsables (puede ser 'ELIA SILVA' o 'ELIA SILVA,DARWIN AQUINO').
    Devuelve lista de ids encontrados y lista de nombres no encontrados.
    """
    ids = []
    no_encontrados = []
    if pd.isna(valor_celda) or str(valor_celda).strip() == '':
        return ids, no_encontrados

    nombres = [n.strip().upper() for n in str(valor_celda).split(',')]
    for nombre_completo in nombres:
        if nombre_completo in catalogo:
            ids.append(catalogo[nombre_completo])
        else:
            no_encontrados.append(nombre_completo)
    return ids, no_encontrados


# ── Carga de un archivo ────────────────────────────────────────────────────────
def cargar_archivo(conn, cursor, archivo_info, productos, presentaciones, responsables):
    path  = archivo_info['path']
    sheet = archivo_info['sheet']
    label = archivo_info['label']

    print(f"\n{'='*60}")
    print(f"📂 Procesando: {label}")
    print(f"{'='*60}")

    if not os.path.exists(path):
        print(f"❌ No se encontró el archivo: {path}")
        return 0, 0

    df = pd.read_excel(path, sheet_name=sheet)
    # Normalizar nombres de columnas (quitar espacios, mayúsculas)
    df.columns = [c.strip().upper() for c in df.columns]
    print(f"📊 Filas leídas: {len(df)}")
    print(f"📋 Columnas:    {list(df.columns)}\n")

    insertados   = 0
    errores      = 0
    resp_faltantes = set()
    prod_faltantes = set()
    pres_faltantes = set()

    for idx, row in df.iterrows():
        try:
            fecha       = row['FECHA']
            producto    = str(row['PRODUCTO']).strip().upper()
            presentacion = str(row['PRESENTACION']).strip().upper()
            cantidad    = int(row['CANTIDAD'])
            responsable_raw = row.get('RESPONSABLE ', row.get('RESPONSABLE', ''))

            # Convertir fecha
            if isinstance(fecha, str):
                fecha_obj = pd.to_datetime(fecha, dayfirst=False).date()
            else:
                fecha_obj = fecha.date() if hasattr(fecha, 'date') else fecha

            # Resolver IDs
            id_producto = productos.get(producto)
            if not id_producto:
                prod_faltantes.add(producto)
                errores += 1
                continue

            id_presentacion = presentaciones.get(presentacion)
            if not id_presentacion:
                pres_faltantes.add(presentacion)
                errores += 1
                continue

            # Insertar producción
            cursor.execute("""
                INSERT INTO produccion (fecha, id_producto, id_presentacion, cantidad)
                VALUES (%s, %s, %s, %s)
            """, (fecha_obj, id_producto, id_presentacion, cantidad))
            id_produccion = cursor.lastrowid

            # Insertar responsables
            ids_resp, no_encontrados = parsear_responsables(responsable_raw, responsables, idx)
            for nf in no_encontrados:
                resp_faltantes.add(nf)

            for id_r in ids_resp:
                cursor.execute("""
                    INSERT INTO produccion_responsable (id_produccion, id_responsable)
                    VALUES (%s, %s)
                """, (id_produccion, id_r))

            insertados += 1

            if insertados % 100 == 0:
                conn.commit()
                print(f"  📈 {insertados} registros insertados...")

        except Exception as e:
            errores += 1
            print(f"  ⚠️  Error fila {idx+2}: {e}")
            continue

    conn.commit()

    # Resumen del archivo
    print(f"\n  ✅ Insertados:  {insertados}")
    print(f"  ❌ Errores:    {errores}")

    if prod_faltantes:
        print(f"\n  ⚠️  Productos NO encontrados en BD ({len(prod_faltantes)}):")
        for p in sorted(prod_faltantes):
            print(f"     · {p}")

    if pres_faltantes:
        print(f"\n  ⚠️  Presentaciones NO encontradas en BD ({len(pres_faltantes)}):")
        for p in sorted(pres_faltantes):
            print(f"     · {p}")

    if resp_faltantes:
        print(f"\n  ⚠️  Responsables NO encontrados en BD ({len(resp_faltantes)}):")
        for r in sorted(resp_faltantes):
            print(f"     · {r}")

    return insertados, errores


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("🚀 CARGA DE PRODUCCIÓN DESDE EXCEL")
    print("=" * 60)

    conn = None
    try:
        conn   = conectar()
        cursor = conn.cursor()

        # Cargar catálogos una sola vez
        productos     = cargar_catalogo_productos(cursor)
        presentaciones = cargar_catalogo_presentaciones(cursor)
        responsables  = cargar_catalogo_responsables(cursor)

        print(f"📦 Productos en BD:      {len(productos)}")
        print(f"📐 Presentaciones en BD: {len(presentaciones)}")
        print(f"👥 Responsables en BD:   {len(responsables)}")

        total_ins = 0
        total_err = 0

        for archivo in ARCHIVOS:
            ins, err = cargar_archivo(conn, cursor, archivo, productos, presentaciones, responsables)
            total_ins += ins
            total_err += err

        # Estado final de la tabla producción
        cursor.execute("SELECT COUNT(*), MIN(fecha), MAX(fecha) FROM produccion")
        total, f_min, f_max = cursor.fetchone()

        print(f"\n{'='*60}")
        print(f"🎉 RESUMEN TOTAL")
        print(f"{'='*60}")
        print(f"  ✅ Total insertados:  {total_ins}")
        print(f"  ❌ Total errores:    {total_err}")
        print(f"\n  📊 Registros en tabla produccion: {total}")
        print(f"  📅 Fecha mínima: {f_min}")
        print(f"  📅 Fecha máxima: {f_max}")

    except Error as e:
        print(f"\n❌ Error de base de datos: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("\n🔌 Conexión cerrada")


if __name__ == '__main__':
    main()
