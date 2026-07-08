import mysql.connector
from mysql.connector import Error

def conectar_mysql():
    try:
        # Configurações da conexão
        conexao = mysql.connector.connect(
            host="localhost",          # ou IP do servidor (ex: "192.168.1.100")
            user="root",        # seu usuário do MySQL
            password="root",      # senha do usuário
            database="ficha19"   # nome do banco de dados (opcional)
        )

        if conexao.is_connected():
            return conexao
                
    except Error as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        return None

# Executar a função
if __name__ == "__main__":
    conectar_mysql()