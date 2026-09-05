import mysql.connector
from mysql.connector import Error


# Cria a conexão entre o sistema e o banco de dados MySQL.
# Essa função é utilizada pelos módulos do eDOC
# sempre que é necessário consultar ou alterar informações.
def conectar_mysql():

    try:

        # Configura os dados de acesso ao banco de dados.
        # O sistema utiliza o banco "ficha19", onde ficam
        # armazenadas informações de alunos, usuários e documentos.
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="ficha19"
        )


        # Verifica se a conexão foi estabelecida corretamente.
        if conexao.is_connected():

            return conexao


    # Caso ocorra algum erro na conexão,
    # informa o problema e retorna vazio.
    except Error as e:

        print(f"Erro ao conectar ao MySQL: {e}")

        return None
    