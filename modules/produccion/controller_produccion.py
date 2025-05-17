from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

# Crear el blueprint
produccion_bp = Blueprint('produccion', __name__)

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

@produccion_bp.route('/')
def index():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produccion ORDER BY fecha DESC")
    registros = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('produccion/index.html', registros=registros)

@produccion_bp.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO produccion (fecha, codigo, producto, presentacion, cantidad, unidad, responsables)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            request.form['fecha'],
            request.form['codigo'],
            request.form['producto'],
            request.form['presentacion'],
            int(request.form['cantidad']),
            request.form['unidad'],
            request.form['responsables']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('produccion.index'))
    return render_template('produccion/agregar.html')

@produccion_bp.route('/eliminar/<int:id>')
def eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produccion WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('produccion.index'))
