import mysql.connector
from mysql.connector import Error

def conectar_mysql():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="ficha19"
        )

        if conexao.is_connected():
            return conexao

    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None
