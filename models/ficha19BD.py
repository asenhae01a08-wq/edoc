from datetime import date, datetime
from decimal import Decimal

from models.conexaoBD import conectar_mysql


def _valor_seguro(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (date, datetime)):
        return valor.strftime("%d/%m/%Y")
    return valor


def _registro_seguro(registro):
    if not registro:
        return registro
    return {chave: _valor_seguro(valor) for chave, valor in registro.items()}


def _lista_segura(registros):
    return [_registro_seguro(registro) for registro in registros]


def _curso_id_por_texto(turma=None, curso=None):
    texto = f"{turma or ''} {curso or ''}".upper()
    if "TDS" in texto or "DESENVOLVIMENTO DE SISTEMAS" in texto:
        return 1
    if "MKT" in texto or "MARKETING" in texto:
        return 2
    return None


def _limpar_disciplinas_antigas(cursor, aluno_id, historico_id):
    cursor.execute(
        "DELETE FROM historico_escolar_anual_base_comum WHERE historico_geral_id = %s",
        (historico_id,),
    )
    cursor.execute(
        "DELETE FROM historico_escolar_anual_itinerario_formativo WHERE historico_geral_id = %s",
        (historico_id,),
    )

    cursor.execute(
        "SELECT disciplina_id FROM aluno_disciplina_base_comum WHERE aluno_id = %s",
        (aluno_id,),
    )
    ids_base = [linha["disciplina_id"] for linha in cursor.fetchall()]

    cursor.execute(
        "DELETE FROM aluno_disciplina_base_comum WHERE aluno_id = %s",
        (aluno_id,),
    )

    for disciplina_id in ids_base:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM aluno_disciplina_base_comum WHERE disciplina_id = %s",
            (disciplina_id,),
        )
        if cursor.fetchone()["total"] == 0:
            cursor.execute(
                "DELETE FROM disciplinas_anuais_base_comum WHERE id = %s",
                (disciplina_id,),
            )

    cursor.execute(
        "SELECT disciplina_id FROM aluno_disciplina_itinerario WHERE aluno_id = %s",
        (aluno_id,),
    )
    ids_itinerario = [linha["disciplina_id"] for linha in cursor.fetchall()]

    cursor.execute(
        "DELETE FROM aluno_disciplina_itinerario WHERE aluno_id = %s",
        (aluno_id,),
    )

    for disciplina_id in ids_itinerario:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM aluno_disciplina_itinerario WHERE disciplina_id = %s",
            (disciplina_id,),
        )
        if cursor.fetchone()["total"] == 0:
            cursor.execute(
                "DELETE FROM disciplinas_anuais_itinerario_formativo WHERE id = %s",
                (disciplina_id,),
            )


def salvar_importacao_pdf(dados):
    """Salva/atualiza aluno e histórico usando apenas as tabelas reais do banco."""
    aluno_pdf = dados.get("aluno", {})
    historico = dados.get("historico", {})
    base_comum = dados.get("base_comum", [])
    itinerario = dados.get("itinerario", [])

    matricula = aluno_pdf.get("matricula")
    if not matricula:
        raise ValueError("A matrícula não foi encontrada no PDF.")

    conexao = conectar_mysql()
    if conexao is None:
        raise RuntimeError("Não foi possível conectar ao banco de dados.")

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM alunos WHERE matricula = %s LIMIT 1",
            (matricula,),
        )
        aluno_existente = cursor.fetchone()

        campos_permitidos = {
            "nome": "nome",
            "data_nascimento": "data_nascimento",
            "cpf": "cpf",
            "rg": "rg",
            "orgao_expedidor": "orgao_expedidor",
            "nacionalidade": "nacionalidade",
            "nome_pai": "nome_pai",
            "nome_mae": "nome_mae",
            "endereco": "endereco",
            "serie": "serie",
            "email": "email",
            "id_turma": "id_turma",
        }

        if aluno_existente:
            atualizacoes = []
            valores = []

            for chave_pdf, coluna in campos_permitidos.items():
                valor = aluno_pdf.get(chave_pdf)
                if valor not in (None, ""):
                    atualizacoes.append(f"{coluna} = %s")
                    valores.append(valor)

            curso_id = _curso_id_por_texto(
                aluno_pdf.get("id_turma"),
                aluno_pdf.get("curso"),
            )
            if curso_id:
                atualizacoes.append("curso_id = %s")
                valores.append(curso_id)

            atualizacoes.append("status_ficha19 = 'Pronta para emissão'")

            valores.append(aluno_existente["id"])
            cursor.execute(
                f"UPDATE alunos SET {', '.join(atualizacoes)} WHERE id = %s",
                tuple(valores),
            )
            aluno_id = aluno_existente["id"]

        else:
            curso_id = _curso_id_por_texto(
                aluno_pdf.get("id_turma"),
                aluno_pdf.get("curso"),
            )
            senha_inicial = matricula[::-1]

            cursor.execute(
                """
                INSERT INTO alunos (
                    nome,
                    matricula,
                    data_nascimento,
                    id_turma,
                    cpf,
                    rg,
                    orgao_expedidor,
                    nacionalidade,
                    nome_pai,
                    nome_mae,
                    endereco,
                    serie,
                    escola_id,
                    curso_id,
                    primeiro_login,
                    email,
                    senha,
                    status_ficha19
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, 1, %s, 1, %s, %s,
                    'Pronta para emissão'
                )
                """,
                (
                    aluno_pdf.get("nome"),
                    matricula,
                    aluno_pdf.get("data_nascimento"),
                    aluno_pdf.get("id_turma"),
                    aluno_pdf.get("cpf"),
                    aluno_pdf.get("rg"),
                    aluno_pdf.get("orgao_expedidor"),
                    aluno_pdf.get("nacionalidade") or "Brasileira",
                    aluno_pdf.get("nome_pai"),
                    aluno_pdf.get("nome_mae"),
                    aluno_pdf.get("endereco"),
                    aluno_pdf.get("serie"),
                    curso_id,
                    aluno_pdf.get("email"),
                    senha_inicial,
                ),
            )
            aluno_id = cursor.lastrowid

        # O registro em historico_escolar_geral também funciona como marcador
        # de que houve uma importação real da Ficha 19 para esse aluno.
        cursor.execute(
            """
            SELECT id
            FROM historico_escolar_geral
            WHERE aluno_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (aluno_id,),
        )
        historico_existente = cursor.fetchone()

        id_historico_escolar = historico.get("id_historico_escolar") or f"EDOC-{matricula}"
        resultado_final = historico.get("resultado_final")
        data_conclusao = historico.get("data_conclusao")

        if historico_existente:
            historico_id = historico_existente["id"]
            cursor.execute(
                """
                UPDATE historico_escolar_geral
                SET id_historico_escolar = %s,
                    resultado_final = %s,
                    data_conclusao = %s
                WHERE id = %s
                """,
                (
                    id_historico_escolar,
                    resultado_final,
                    data_conclusao,
                    historico_id,
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO historico_escolar_geral (
                    aluno_id,
                    id_historico_escolar,
                    resultado_final,
                    data_conclusao
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    aluno_id,
                    id_historico_escolar,
                    resultado_final,
                    data_conclusao,
                ),
            )
            historico_id = cursor.lastrowid

        _limpar_disciplinas_antigas(cursor, aluno_id, historico_id)

        for item in base_comum:
            if not item.get("nome"):
                continue

            cursor.execute(
                """
                INSERT INTO disciplinas_anuais_base_comum (
                    nome,
                    nota,
                    ano_letivo,
                    resultado,
                    frequencia_percentual,
                    carga_horaria_horas_aula,
                    carga_horaria_relogio,
                    carga_horaria_total_anual
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    item.get("nome"),
                    item.get("nota"),
                    item.get("ano_letivo"),
                    item.get("resultado"),
                    item.get("frequencia_percentual"),
                    item.get("carga_horaria_horas_aula"),
                    item.get("carga_horaria_relogio"),
                    item.get("carga_horaria_total_anual"),
                ),
            )
            disciplina_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO aluno_disciplina_base_comum (aluno_id, disciplina_id) VALUES (%s, %s)",
                (aluno_id, disciplina_id),
            )
            cursor.execute(
                """
                INSERT INTO historico_escolar_anual_base_comum (
                    historico_geral_id,
                    disciplina_id,
                    percentual_frequencia_anual,
                    carga_horaria_horas_aula
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    historico_id,
                    disciplina_id,
                    item.get("frequencia_percentual"),
                    item.get("carga_horaria_horas_aula"),
                ),
            )

        for item in itinerario:
            if not item.get("nome"):
                continue

            cursor.execute(
                """
                INSERT INTO disciplinas_anuais_itinerario_formativo (
                    nome,
                    abreviacao,
                    tipo,
                    nota,
                    resultado_final,
                    periodo_letivo,
                    frequencia,
                    carga_horaria,
                    carga_horaria_horas_aula,
                    carga_horaria_relogio
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    item.get("nome"),
                    item.get("abreviacao"),
                    item.get("tipo"),
                    item.get("nota"),
                    item.get("resultado_final"),
                    item.get("periodo_letivo"),
                    item.get("frequencia"),
                    item.get("carga_horaria"),
                    item.get("carga_horaria_horas_aula") or item.get("carga_horaria"),
                    item.get("carga_horaria_relogio"),
                ),
            )
            disciplina_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO aluno_disciplina_itinerario (aluno_id, disciplina_id) VALUES (%s, %s)",
                (aluno_id, disciplina_id),
            )
            cursor.execute(
                """
                INSERT INTO historico_escolar_anual_itinerario_formativo (
                    historico_geral_id,
                    disciplina_id,
                    percentual_frequencia_anual,
                    carga_horaria_horas_aula
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    historico_id,
                    disciplina_id,
                    item.get("frequencia"),
                    item.get("carga_horaria_horas_aula") or item.get("carga_horaria"),
                ),
            )

        conexao.commit()
        return aluno_id

    except Exception:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()


def buscar_dados_ficha_por_aluno(aluno_id):
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
                e.estado AS escola_estado
            FROM alunos a
            LEFT JOIN cursos c ON c.id = a.curso_id
            LEFT JOIN escolas e ON e.id = a.escola_id
            WHERE a.id = %s
            LIMIT 1
            """,
            (aluno_id,),
        )
        aluno = cursor.fetchone()

        if aluno is None:
            return None

        cursor.execute(
            """
            SELECT *
            FROM historico_escolar_geral
            WHERE aluno_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (aluno_id,),
        )
        historico = cursor.fetchone()

        cursor.execute(
            """
            SELECT d.*
            FROM disciplinas_anuais_base_comum d
            INNER JOIN aluno_disciplina_base_comum ad
                ON ad.disciplina_id = d.id
            WHERE ad.aluno_id = %s
            ORDER BY d.ano_letivo, d.nome
            """,
            (aluno_id,),
        )
        base_comum = cursor.fetchall()

        cursor.execute(
            """
            SELECT d.*
            FROM disciplinas_anuais_itinerario_formativo d
            INNER JOIN aluno_disciplina_itinerario ad
                ON ad.disciplina_id = d.id
            WHERE ad.aluno_id = %s
            ORDER BY d.periodo_letivo, d.nome
            """,
            (aluno_id,),
        )
        itinerario = cursor.fetchall()

        return {
            "aluno": _registro_seguro(aluno),
            "historico": _registro_seguro(historico),
            "base_comum": _lista_segura(base_comum),
            "itinerario": _lista_segura(itinerario),
        }

    finally:
        cursor.close()
        conexao.close()
