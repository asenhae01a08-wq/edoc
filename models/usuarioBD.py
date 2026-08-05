

from models.conexaoBD import conectar_mysql
import mysql.connector


def verificarLogin(email, senha):
    conexao = conectar_mysql()

    if conexao is None:
        return None

    cursor = conexao.cursor(dictionary=True)

    query = """
        SELECT *
        FROM usuarios
        WHERE email = %s
          AND senha = %s
          AND status = 'Ativo'
        LIMIT 1
    """

    cursor.execute(query, (email, senha))
    usuario = cursor.fetchone()

    print("Email:", email)
    print("Senha:", senha)
    print("Usuario:", usuario)

    cursor.close()
    conexao.close()

    return usuario


def buscar_aluno(email):
    conexao = conectar_mysql()

    if conexao is None:
        return None

    cursor = conexao.cursor(dictionary=True)

    query = """
        SELECT
            id,
            nome,
            matricula,
            id_turma,
            status_ficha19
        FROM alunos
        WHERE email = %s
        LIMIT 1
    """

    cursor.execute(query, (email,))
    aluno = cursor.fetchone()

    print("Aluno encontrado:", aluno)

    cursor.close()
    conexao.close()

    return aluno