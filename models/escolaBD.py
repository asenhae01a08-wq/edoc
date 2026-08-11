from models.conexaoBD import conectar_mysql


def buscar_escola():

    conexao = conectar_mysql()

    if conexao is None:
        return None

    cursor = conexao.cursor(
        dictionary=True
    )

    query = """
        SELECT *
        FROM escolas
        WHERE id = 1
        LIMIT 1
    """

    cursor.execute(query)

    escola = cursor.fetchone()

    cursor.close()
    conexao.close()

    return escola