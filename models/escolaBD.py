from models.conexaoBD import conectar_mysql


# Importa a função responsável pela conexão com o banco de dados.
# Este módulo utiliza essa conexão para buscar informações
# institucionais utilizadas na geração da Ficha 19.


def buscar_escola():

    # Cria a conexão com o banco de dados MySQL.
    conexao = conectar_mysql()

    # Caso não seja possível conectar ao banco,
    # retorna vazio para evitar erro no sistema.
    if conexao is None:
        return None


    cursor = conexao.cursor(
        dictionary=True
    )


    # Consulta os dados da escola cadastrada no sistema.
    # Essas informações são utilizadas na composição da Ficha 19,
    # como nome, endereço e dados institucionais.
    query = """
        SELECT *
        FROM escolas
        WHERE id = 1
        LIMIT 1
    """


    cursor.execute(query)


    # Recupera os dados da escola encontrada no banco.
    escola = cursor.fetchone()


    # Fecha o cursor e a conexão após finalizar a consulta,
    # liberando os recursos utilizados.
    cursor.close()
    conexao.close()


    return escola