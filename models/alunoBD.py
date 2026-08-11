from models.conexaoBD import conectar_mysql


def buscar_alunos_por_turma(id_turma):
    conexao = conectar_mysql()

    if conexao is None:
        return []

    cursor = conexao.cursor(dictionary=True)

    query = """
        SELECT
            id,
            nome,
            matricula,
            id_turma,
            status_ficha19
        FROM alunos
        WHERE id_turma = %s
        ORDER BY nome
    """

    cursor.execute(query, (id_turma,))
    alunos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return alunos