import pandas as pd
import mysql.connector
import re

# 1. Cargar Excel
df = pd.read_excel(r"c:\SI\Chocopasion\chocopasion.xlsx")
df.columns = [col.strip().upper() for col in df.columns]

# 2. Normalizar FECHA
df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True).dt.strftime('%Y-%m-%d')

# 3. Limpiar y convertir CANTIDAD
df['CANTIDAD'] = df['CANTIDAD'].astype(str).str.extract(r'([\d\.,]+)')[0]
df['CANTIDAD'] = df['CANTIDAD'].str.replace(',', '.', regex=False)
df['CANTIDAD'] = pd.to_numeric(df['CANTIDAD'], errors='coerce')
df = df.dropna(subset=['CANTIDAD'])
df['CANTIDAD'] = df['CANTIDAD'].astype(int)

# 4. Normalizar PRESENTACION
def normalizar_presentacion(pres):
    pres = str(pres).strip().upper()
    if re.match(r'^\d+G$', pres):
        return pres[:-1] + ' GR'
    if '100ML' in pres or re.match(r'^\d+ML$', pres):
        return 'UNIDAD'
    return pres

df['PRESENTACION'] = df['PRESENTACION'].apply(normalizar_presentacion)

# 5. Conexión MySQL
conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="",
    database="chocopasion1"
)
cursor = conn.cursor(dictionary=True)

# ...existing code...

def buscar_responsable(nombre, apellido):
    cursor.execute("SELECT id_responsable FROM responsables WHERE nombre = %s AND apellido = %s", (nombre, apellido))
    return cursor.fetchone()

try:
    for _, row in df.iterrows():
        # Buscar id_producto
        cursor.execute("SELECT id_producto FROM productos WHERE nombre = %s", (row['PRODUCTO'],))
        prod = cursor.fetchone()
        if not prod:
            print(f"❌ Producto no encontrado: {row['PRODUCTO']}")
            continue
        id_producto = prod['id_producto']

        # Buscar id_presentacion
        cursor.execute("SELECT id_presentacion FROM presentaciones WHERE descripcion = %s", (row['PRESENTACION'],))
        pres = cursor.fetchone()
        if not pres:
            print(f"❌ Presentación no encontrada: {row['PRESENTACION']}")
            continue
        id_presentacion = pres['id_presentacion']

        # Insertar en produccion
        cursor.execute("""
            INSERT INTO produccion (fecha, id_producto, id_presentacion, cantidad)
            VALUES (%s, %s, %s, %s)
        """, (
            row['FECHA'],
            id_producto,
            id_presentacion,
            row['CANTIDAD']
        ))
        id_produccion = cursor.lastrowid

        # Procesar responsables
        responsables = [r.strip() for r in str(row['RESPONSABLE']).split(',')]
        for responsable in responsables:
            partes = responsable.split()
            if len(partes) >= 2:
                nombre = partes[0].upper()
                apellido = ' '.join(partes[1:]).upper()
                resp = buscar_responsable(nombre, apellido)
                if resp:
                    cursor.execute("""
                        INSERT IGNORE INTO produccion_responsable (id_produccion, id_responsable)
                        VALUES (%s, %s)
                    """, (id_produccion, resp['id_responsable']))
                else:
                    print(f"❌ Responsable no encontrado: {responsable}")
            else:
                print(f"❌ Formato de responsable inválido: {responsable}")

    conn.commit()
    print("✔ Registros importados correctamente a MySQL.")

# ...existing code...

except Exception as e:
    print(f"❌ Error durante la importación: {str(e)}")
    conn.rollback()

finally:
    cursor.close()
    conn.close()