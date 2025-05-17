import mysql.connector
from flask import g
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'chocopasion'),
            port=int(os.getenv('DB_PORT', '3306')),
            auth_plugin='mysql_native_password'
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
