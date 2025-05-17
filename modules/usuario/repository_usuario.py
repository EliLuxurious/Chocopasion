from infrastructure.database import get_db

class UsuarioRepository:

    @staticmethod
    def buscar_por_username(username):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        return cursor.fetchone()

    @staticmethod
    def insertar(data):
        db = get_db()
        cursor = db.cursor()
        query = "INSERT INTO usuarios (username, password) VALUES (%s, %s)"
        cursor.execute(query, (data['username'], data['password']))
        db.commit()
