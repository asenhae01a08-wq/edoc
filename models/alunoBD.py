from models.conexaoBD import conectar_mysql


# ==========================================================
# BUSCAR ALUNOS POR TURMA
# ==========================================================

def buscar_alunos_por_turma(turma):

    conexao = conectar_mysql()

    if conexao is None:
        return []

    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                id,
                nome,
                matricula,
                id_turma,
                status_ficha19,

                NULL AS curso_nome,
                0 AS possui_ficha

            FROM alunos

            WHERE id_turma = %s

            ORDER BY nome
            """,
            (turma,),
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        conexao.close()


# ==========================================================
# BUSCAR TODOS OS ALUNOS
# ==========================================================

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

                NULL AS curso_nome,
                0 AS possui_ficha

            FROM alunos a

            ORDER BY a.nome
            """
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        conexao.close()


# ==========================================================
# BUSCAR ALUNO POR ID
# ==========================================================

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

                NULL AS curso_nome,
                NULL AS escola_nome,
                NULL AS escola_cidade,
                NULL AS escola_estado,

                0 AS possui_ficha

            FROM alunos a

            WHERE a.id = %s

            LIMIT 1
            """,
            (id_aluno,),
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        conexao.close()


# ==========================================================
# BUSCAR ALUNO POR MATRÍCULA
# ==========================================================

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


# ==========================================================
# BUSCAR ALUNO POR EMAIL
# ==========================================================

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


# ==========================================================
# CADASTRAR ALUNO
# ==========================================================

def cadastrar_aluno(
    nome,
    matricula,
    cpf,
    email,
    data_nascimento,
    turma
):

    conexao = conectar_mysql()

    if conexao is None:

        return (
            False,
            "Não foi possível conectar ao banco de dados.",
            None
        )


    cursor = conexao.cursor(dictionary=True)


    try:

        # ==================================================
        # CONFERE SE JÁ EXISTE
        # ==================================================

        cursor.execute(
            """
            SELECT
                id,
                matricula,
                cpf,
                email

            FROM alunos

            WHERE matricula = %s
               OR cpf = %s
               OR email = %s

            LIMIT 1
            """,
            (
                matricula,
                cpf,
                email
            ),
        )


        existente = cursor.fetchone()


        if existente:

            return (
                False,
                "Já existe um aluno com essa matrícula, CPF ou e-mail.",
                None
            )


        # ==================================================
        # CURSO
        # ==================================================

        curso_id = (
            1
            if "TDS" in turma.upper()

            else 2
            if "MKT" in turma.upper()

            else None
        )


        # ==================================================
        # SENHA INICIAL
        # MATRÍCULA INVERTIDA
        # ==================================================

        senha_inicial = matricula[::-1]


        # ==================================================
        # INSERE ALUNO
        # ==================================================

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

            VALUES (

                %s,
                %s,
                %s,
                %s,
                %s,
                1,
                %s,
                NULL,
                %s,
                %s,
                'Em fabricação',
                'Aluno'

            )
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


        return (
            True,
            "Aluno cadastrado com sucesso.",
            senha_inicial
        )


    except Exception:

        conexao.rollback()

        raise


    finally:

        cursor.close()
        conexao.close()


# ==========================================================
# PESQUISAR ALUNO
# NOME OU MATRÍCULA
# ==========================================================

def buscar_alunos_por_pesquisa(termo):

    if not termo:
        return []


    termo = termo.strip()


    if not termo:
        return []


    conexao = conectar_mysql()


    if conexao is None:
        return []


    cursor = conexao.cursor(dictionary=True)


    try:

        pesquisa = f"%{termo}%"


        cursor.execute(
            """
            SELECT

                id,
                nome,
                matricula,
                id_turma,
                status_ficha19,

                NULL AS curso_nome,
                0 AS possui_ficha

            FROM alunos

            WHERE
                nome LIKE %s
                OR CAST(matricula AS CHAR) LIKE %s

            ORDER BY nome

            LIMIT 30
            """,
            (
                pesquisa,
                pesquisa,
            ),
        )


        return cursor.fetchall()


    finally:

        cursor.close()
        conexao.close()