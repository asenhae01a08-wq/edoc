from models.conexaoBD import conectar_mysql


# ==========================================================
# BUSCAR ALUNOS POR TURMA
# ==========================================================

# Retorna os alunos pertencentes a uma turma específica.
# Usado nas telas de turmas e gerenciamento dos estudantes.
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
# BUSCAR ALUNOS POR PESQUISA
# ==========================================================

# Pesquisa alunos por nome, matrícula, CPF ou e-mail.
# É utilizada pela pesquisa ao vivo da tela "Turmas e alunos".
def buscar_alunos_por_pesquisa(termo):

    conexao = conectar_mysql()

    if conexao is None:
        return []

    cursor = conexao.cursor(dictionary=True)

    try:

        termo = str(
            termo or ""
        ).strip()

        if not termo:
            return []

        termo_busca = f"%{termo}%"

        cursor.execute(
            """
            SELECT
                id,
                nome,
                matricula,
                id_turma,
                cpf,
                email,
                data_nascimento,
                status_ficha19

            FROM alunos

            WHERE
                nome LIKE %s
                OR matricula LIKE %s
                OR cpf LIKE %s
                OR email LIKE %s
                OR id_turma LIKE %s

            ORDER BY nome
            """,
            (
                termo_busca,
                termo_busca,
                termo_busca,
                termo_busca,
                termo_busca,
            ),
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        conexao.close()


# ==========================================================
# BUSCAR TODOS OS ALUNOS
# ==========================================================

# Busca todos os estudantes cadastrados no sistema.
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

# Busca um aluno pelo identificador único do banco.
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

# Localiza aluno utilizando a matrícula.
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

# Busca aluno pelo email cadastrado.
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

# Realiza o cadastro de um novo estudante no banco.
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
            "Não foi possível conectar ao banco.",
            None
        )

    cursor = conexao.cursor(dictionary=True)

    try:

        # ==================================================
        # VERIFICA DUPLICIDADE
        # ==================================================

        cursor.execute(
            """
            SELECT id
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
                "Aluno já cadastrado.",
                None
            )

        # ==================================================
        # CADASTRA O ALUNO
        #
        # O valor de turma é gravado exatamente como
        # recebido pelo formulário:
        #
        # 3º TDS A
        # 3º TDS B
        # 3º MKT A
        # 3º MKT B
        # ==================================================

        cursor.execute(
            """
            INSERT INTO alunos
            (
                nome,
                matricula,
                cpf,
                email,
                data_nascimento,
                id_turma
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                nome,
                matricula,
                cpf,
                email,
                data_nascimento,
                turma
            )
        )

        conexao.commit()

        return (
            True,
            "Aluno cadastrado com sucesso.",
            cursor.lastrowid
        )

    except Exception:

        conexao.rollback()

        raise

    finally:

        cursor.close()
        conexao.close()