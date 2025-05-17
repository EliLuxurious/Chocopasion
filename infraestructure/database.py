from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def conectar():
    try:
        print("Intentando conectar a la base de datos...")
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='chocopasion',
            port=3306,
            auth_plugin='mysql_native_password'
        )
        print("✅ Conexión exitosa a la base de datos")
        return conn
    except Error as err:
        print(f"❌ Error al conectar a la base de datos: {err}")
        if err.errno == 1045:
            print("Error: Usuario o contraseña incorrectos")
        elif err.errno == 1049:
            print("Error: La base de datos no existe")
        elif err.errno == 2003:
            print("Error: No se puede conectar al servidor MySQL")
        raise

@app.route('/')
def index():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produccion ORDER BY fecha DESC")
    registros = cursor.fetchall()
    conn.close()
    return render_template("index.html", registros=registros)

@app.route('/agregar', methods=['GET', 'POST'])
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
        conn.close()
        return redirect(url_for('index'))
    return render_template("agregar.html")

@app.route('/eliminar/<int:id>')
def eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produccion WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

