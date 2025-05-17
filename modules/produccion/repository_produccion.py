from flask import g, jsonify
from infrastructure.database import get_db

class ProduccionRepository:

    @staticmethod
    def insertar(data):
        db = get_db()
        cursor = db.cursor()
        query = """
            INSERT INTO produccion (fecha, producto_id, cantidad, unidad, responsable_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['fecha'],
            data['producto_id'],
            data['cantidad'],
            data['unidad'],
            data['responsable_id']
        ))
        db.commit()
        return {"mensaje": "Producción registrada con éxito"}, 201

    @staticmethod
    def listar():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.id, p.fecha, pr.nombre AS producto, p.cantidad, p.unidad, u.nombre AS responsable
            FROM produccion p
            JOIN productos pr ON p.producto_id = pr.id
            JOIN usuarios u ON p.responsable_id = u.id
            ORDER BY p.fecha DESC
        """)
        resultado = cursor.fetchall()
        return jsonify(resultado)
