from models.conexaoBD import conectar_mysql


def verificarLogin(identificacao, senha):
    """
    Login unificado:
    - matrícula -> tabela alunos
    - e-mail -> primeiro usuarios (profissional), depois alunos
    """
    if not identificacao or not senha:
        return None

    identificacao = identificacao.strip()

    conexao = conectar_mysql()
    if conexao is None:
        return None

    cursor = conexao.cursor(dictionary=True)

    try:
        # Login do aluno por matrícula
        if identificacao.isdigit():
            cursor.execute(
                """
                SELECT
    id,
    nome,
    email,
    matricula,
    primeiro_login
FROM alunos
                WHERE matricula = %s
                  AND senha = %s
                LIMIT 1
                """,
                (identificacao, senha),
            )
            aluno = cursor.fetchone()

            if aluno:
                aluno["cargo_nivel"] = "Aluno"
                aluno["origem"] = "aluno"
                return aluno

            return None

        # Login de profissional por e-mail
        cursor.execute(
            """
            SELECT id, nome, email, cargo_nivel
            FROM usuarios
            WHERE email = %s
              AND senha = %s
              AND status = 'Ativo'
            LIMIT 1
            """,
            (identificacao, senha),
        )
        usuario = cursor.fetchone()

        if usuario:
            usuario["origem"] = "usuario"
            return usuario

        # Também permite aluno entrar usando o e-mail cadastrado
        cursor.execute(
            """
            SELECT id, nome, email, matricula
            FROM alunos
            WHERE email = %s
              AND senha = %s
            LIMIT 1
            """,
            (identificacao, senha),
        )
        aluno = cursor.fetchone()
        
        if aluno:
            aluno["cargo_nivel"] = "Aluno"
            aluno["origem"] = "aluno"
            return aluno

        return None

    finally:
        cursor.close()
        conexao.close()


# Mantém compatibilidade com códigos antigos que importavam buscar_aluno daqui.
def buscar_aluno(email):
    conexao = conectar_mysql()
    if conexao is None:
        return None

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                a.*,
                c.nome AS curso_nome,
                EXISTS(
                    SELECT 1
                    FROM historico_escolar_geral h
                    WHERE h.aluno_id = a.id
                ) AS possui_ficha
            FROM alunos a
            LEFT JOIN cursos c ON c.id = a.curso_id
            WHERE a.email = %s
            LIMIT 1
            """,
            (email,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexao.close()
