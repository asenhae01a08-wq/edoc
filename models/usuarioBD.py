from models.conexaoBD import conectar_mysql


# Importa a função responsável pela conexão com o banco de dados.
# Esse módulo utiliza a conexão para validar usuários e controlar
# os diferentes níveis de acesso do sistema.


def verificarLogin(identificacao, senha):
    """
    Login unificado:
    - matrícula -> tabela alunos
    - e-mail -> primeiro usuarios (profissional), depois alunos
    """

    # Verifica se os campos obrigatórios de autenticação foram preenchidos.
    if not identificacao or not senha:
        return None

    identificacao = identificacao.strip()

    conexao = conectar_mysql()

    if conexao is None:
        return None

    cursor = conexao.cursor(dictionary=True)

    try:

        # Login do aluno utilizando a matrícula.
        # O sistema verifica os dados na tabela de alunos
        # e identifica o perfil como estudante.
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

                # Define o nível de acesso do usuário encontrado.
                # Essa informação é utilizada pelo sistema para
                # liberar as funcionalidades do aluno.
                aluno["cargo_nivel"] = "Aluno"
                aluno["origem"] = "aluno"

                return aluno


            return None


        # Login do profissional utilizando o e-mail.
        # Consulta usuários ativos que possuem permissões administrativas
        # dentro do sistema.
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

            # Identifica a origem do acesso para diferenciar
            # usuários profissionais e alunos.
            usuario["origem"] = "usuario"

            return usuario



        # Também permite que alunos utilizem o e-mail cadastrado
        # como alternativa de acesso ao sistema.
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

            # Define novamente o perfil como aluno para que o sistema
            # aplique as permissões corretas.
            aluno["cargo_nivel"] = "Aluno"
            aluno["origem"] = "aluno"

            return aluno


        return None


    finally:

        # Fecha os recursos utilizados para evitar conexões abertas
        # desnecessariamente no banco de dados.
        cursor.close()
        conexao.close()



# Mantém compatibilidade com códigos antigos que importavam buscar_aluno daqui.
def buscar_aluno(email):

    # Busca informações complementares do estudante,
    # incluindo curso e existência de histórico escolar.
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


        # Retorna os dados encontrados para utilização
        # nas telas do sistema.
        return cursor.fetchone()


    finally:

        cursor.close()
        conexao.close()