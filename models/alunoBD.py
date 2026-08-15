from models.conexaoBD import conectar_mysql


def buscar_alunos_por_turma(turma):
    conexao = conectar_mysql()
    if conexao is None:
        return []

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                a.id,
                a.nome,
                a.matricula,
                a.id_turma,
                a.status_ficha19,
                c.nome AS curso_nome,
                EXISTS(
                    SELECT 1
                    FROM historico_escolar_geral h
                    WHERE h.aluno_id = a.id
                ) AS possui_ficha
            FROM alunos a
            LEFT JOIN cursos c ON c.id = a.curso_id
            WHERE a.id_turma = %s
            ORDER BY a.nome
            """,
            (turma,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conexao.close()


def buscar_todos_alunos():
    conexao = conectar_mysql()
    if conexao is None:
        return []

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
            ORDER BY a.nome
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conexao.close()


def buscar_aluno_por_id(id_aluno):
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
                e.nome AS escola_nome,
                e.cidade AS escola_cidade,
                e.estado AS escola_estado,
                EXISTS(
                    SELECT 1
                    FROM historico_escolar_geral h
                    WHERE h.aluno_id = a.id
                ) AS possui_ficha
            FROM alunos a
            LEFT JOIN cursos c ON c.id = a.curso_id
            LEFT JOIN escolas e ON e.id = a.escola_id
            WHERE a.id = %s
            LIMIT 1
            """,
            (id_aluno,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexao.close()


def buscar_aluno_por_matricula(matricula):
    conexao = conectar_mysql()
    if conexao is None:
        return None

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT *
            FROM alunos
            WHERE matricula = %s
            LIMIT 1
            """,
            (matricula,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexao.close()


def buscar_aluno_por_email(email):
    conexao = conectar_mysql()
    if conexao is None:
        return None

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT *
            FROM alunos
            WHERE email = %s
            LIMIT 1
            """,
            (email,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexao.close()


def cadastrar_aluno(nome, matricula, cpf, email, data_nascimento, turma):
    conexao = conectar_mysql()
    if conexao is None:
        return False, "Não foi possível conectar ao banco de dados.", None

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, matricula, cpf, email
            FROM alunos
            WHERE matricula = %s
               OR cpf = %s
               OR email = %s
            LIMIT 1
            """,
            (matricula, cpf, email),
        )

        existente = cursor.fetchone()
        if existente:
            return False, "Já existe um aluno com essa matrícula, CPF ou e-mail.", None

        curso_id = 1 if "TDS" in turma.upper() else 2 if "MKT" in turma.upper() else None

        # Senha provisória do protótipo: matrícula invertida.
        # O campo primeiro_login já existe no banco para futura troca obrigatória.
        senha_inicial = matricula[::-1]

        cursor.execute(
            """
            INSERT INTO alunos (
                nome,
                matricula,
                data_nascimento,
                id_turma,
                cpf,
                escola_id,
                curso_id,
                primeiro_login,
                email,
                senha,
                status_ficha19,
                cargo_nivel
            )
            VALUES (%s, %s, %s, %s, %s, 1, %s, NULL, %s, %s, 'Em fabricação', 'Aluno')
            """,
            (
                nome,
                matricula,
                data_nascimento,
                turma,
                cpf,
                curso_id,
                email,
                senha_inicial,
            ),
        )

        conexao.commit()
        return True, "Aluno cadastrado com sucesso.", senha_inicial

    except Exception:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()