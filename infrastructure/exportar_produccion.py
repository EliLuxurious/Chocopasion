import pandas as pd
import mysql.connector

# 1. Cargar CSV (usa sep=';' si es necesario)
df = pd.read_csv(r"c:\SI\Chocopasion\Produccion Completa.csv", encoding='latin1', sep=';')
# 2. Normalizar nombres de columnas
df.columns = [col.strip().upper() for col in df.columns]

# 3. Convertir FECHA a formato YYYY-MM-DD
df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True).dt.strftime('%Y-%m-%d')

# 4. Convertir cantidad a int si es float
df['CANTIDAD'] = df['CANTIDAD'].astype(int)

# 5. Conexión MySQL
conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="",
    database="chocopasion"
)
cursor = conn.cursor()

# 6. Insertar registros
try:
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO produccion (fecha, codigo, producto, presentacion, cantidad, unidad, responsables)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row['FECHA'],
            row['CODIGO'],
            row['PRODUCTO'],
            row['PRESENTACION'],
            row['CANTIDAD'],
            row['UNIDAD'],
            row['RESPONSABLE'].strip()
        ))

    conn.commit()
    print("✔ Registros importados correctamente a MySQL.")

except Exception as e:
    print(f"❌ Error durante la importación: {str(e)}")
    conn.rollback()

finally:
    cursor.close()
    conn.close()
