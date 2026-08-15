import json
from datetime import date, datetime
from decimal import Decimal

from models.conexaoBD import conectar_mysql


def _valor_seguro(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (date, datetime)):
        return valor.strftime("%d/%m/%Y")
    return valor



def _nota_segura(valor, contexto=""):
    if valor in (None, "", "-"):
        return None

    try:
        if isinstance(valor, str):
            valor = valor.strip().replace(",", ".")
        nota = float(valor)
    except (TypeError, ValueError):
        raise ValueError(
            f"Nota inválida recebida do PDF"
            f"{' em ' + contexto if contexto else ''}: {valor!r}"
        )

    if nota < 0 or nota > 10:
        raise ValueError(
            f"Nota fora da faixa de 0 a 10"
            f"{' em ' + contexto if contexto else ''}: {nota}."
        )

    return round(nota, 2)


def _percentual_seguro(valor, contexto=""):
    if valor in (None, "", "-"):
        return None

    try:
        if isinstance(valor, str):
            valor = valor.strip().replace("%", "").replace(",", ".")
        percentual = float(valor)
    except (TypeError, ValueError):
        raise ValueError(
            f"Percentual inválido recebido do PDF"
            f"{' em ' + contexto if contexto else ''}: {valor!r}"
        )

    if percentual < 0 or percentual > 100:
        raise ValueError(
            f"Percentual fora da faixa de 0 a 100"
            f"{' em ' + contexto if contexto else ''}: {percentual}."
        )

    return round(percentual, 2)


def _id_alunos_auto_increment(cursor):
    cursor.execute(
        """
        SELECT EXTRA
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'alunos'
          AND COLUMN_NAME = 'id'
        LIMIT 1
        """
    )
    linha = cursor.fetchone()
    return bool(
        linha
        and "auto_increment" in str(linha.get("EXTRA") or "").lower()
    )


def _registro_seguro(registro):
    if not registro:
        return registro
    return {chave: _valor_seguro(valor) for chave, valor in registro.items()}


def _lista_segura(registros):
    return [_registro_seguro(registro) for registro in registros]


def _json_padrao(valor):
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return float(valor)
    raise TypeError(f"Tipo não serializável: {type(valor).__name__}")


def _curso_id_por_texto(turma=None, curso=None):
    texto = f"{turma or ''} {curso or ''}".upper()

    if "TDS" in texto or "DESENVOLVIMENTO DE SISTEMAS" in texto:
        return 1

    if "MKT" in texto or "MARKETING" in texto:
        return 2

    # O PDF oficial pode trazer apenas "ENSINO MÉDIO".
    # Nesse caso NÃO substituímos o curso técnico que já existe no cadastro.
    return None


def _coluna_existe(cursor, tabela, coluna):
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (tabela, coluna),
    )
    return cursor.fetchone()["total"] > 0


def _validar_estrutura(cursor):
    faltando = []

    if not _coluna_existe(cursor, "alunos", "status_ficha19"):
        faltando.append("alunos.status_ficha19")

    if not _coluna_existe(cursor, "historico_escolar_geral", "dados_extras"):
        faltando.append("historico_escolar_geral.dados_extras")

    if not _id_alunos_auto_increment(cursor):
        faltando.append("alunos.id AUTO_INCREMENT")

    if faltando:
        raise RuntimeError(
            "O banco precisa da migração da Ficha 19 oficial. "
            "Execute o arquivo migracao_ficha19_corrigida.sql. "
            "Campos ausentes: " + ", ".join(faltando)
        )


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


def _atualizar_escola(cursor, escola_pdf):
    if not escola_pdf:
        return 1

    nome = escola_pdf.get("nome")
    cidade = escola_pdf.get("cidade")
    estado = escola_pdf.get("estado")

    cursor.execute("SELECT id FROM escolas WHERE id = 1 LIMIT 1")
    existe = cursor.fetchone()

    if existe:
        atualizacoes = []
        valores = []

        if nome:
            atualizacoes.append("nome = %s")
            valores.append(nome.title())

        if cidade:
            atualizacoes.append("cidade = %s")
            valores.append(cidade.title())

        if estado:
            atualizacoes.append("estado = %s")
            valores.append(estado)

        if atualizacoes:
            valores.append(1)
            cursor.execute(
                f"UPDATE escolas SET {', '.join(atualizacoes)} WHERE id = %s",
                tuple(valores),
            )

        return 1

    cursor.execute(
        """
        INSERT INTO escolas (nome, cidade, estado)
        VALUES (%s, %s, %s)
        """,
        (
            nome.title() if nome else None,
            cidade.title() if cidade else None,
            estado,
        ),
    )

    return cursor.lastrowid


def salvar_importacao_pdf(dados):
    """
    Salva o histórico oficial.

    Os dados que já possuem colunas normalizadas continuam sendo gravados nas
    tabelas existentes. Informações oficiais que não possuem coluna própria
    (endereço/autorização da escola, resumo anual, trilhas, data/local etc.)
    são preservadas integralmente em historico_escolar_geral.dados_extras.
    """
    aluno_pdf = dados.get("aluno", {})
    escola_pdf = dados.get("escola", {})
    historico = dados.get("historico", {})
    base_comum = dados.get("base_comum", [])
    itinerario = dados.get("itinerario", [])
    extras = dados.get("extras", {})

    matricula = str(aluno_pdf.get("matricula") or "").strip()

    if not matricula:
        raise ValueError("A matrícula não foi encontrada no PDF oficial.")

    if not matricula.isdigit() or len(matricula) != 7:
        raise ValueError(
            f"A matrícula extraída precisa ter 7 números. Valor recebido: {matricula!r}."
        )

    conexao = conectar_mysql()

    if conexao is None:
        raise RuntimeError("Não foi possível conectar ao banco de dados.")

    cursor = conexao.cursor(dictionary=True)

    try:
        _validar_estrutura(cursor)

        escola_id = _atualizar_escola(cursor, escola_pdf)

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

            # O endereço presente no PDF oficial é o endereço da ESCOLA.
            # Não sobrescrevemos alunos.endereco com ele.
            atualizacoes.append("escola_id = %s")
            valores.append(escola_id)

            curso_id = _curso_id_por_texto(
                aluno_pdf.get("id_turma"),
                aluno_pdf.get("curso"),
            )

            if curso_id:
                atualizacoes.append("curso_id = %s")
                valores.append(curso_id)

            atualizacoes.append("status_ficha19 = 'Pronta para emissão'")
            atualizacoes.append("cargo_nivel = 'Aluno'")

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
                    status_ficha19,
                    cargo_nivel
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, NULL, %s, %s, %s, NULL, %s, %s,
                    'Pronta para emissão', 'Aluno'
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
                    aluno_pdf.get("serie"),
                    escola_id,
                    curso_id,
                    aluno_pdf.get("email"),
                    senha_inicial,
                ),
            )

            aluno_id = cursor.lastrowid

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

        id_historico_escolar = (
            historico.get("id_historico_escolar")
            or f"EDOC-{matricula}"
        )

        resultado_final = historico.get("resultado_final")
        if resultado_final:
            resultado_final = str(resultado_final).strip()[:30]

        data_conclusao = historico.get("data_conclusao")

        dados_extras_json = json.dumps(
            extras,
            ensure_ascii=False,
            default=_json_padrao,
        )

        if historico_existente:
            historico_id = historico_existente["id"]

            cursor.execute(
                """
                UPDATE historico_escolar_geral
                SET id_historico_escolar = %s,
                    resultado_final = %s,
                    data_conclusao = %s,
                    dados_extras = %s
                WHERE id = %s
                """,
                (
                    id_historico_escolar,
                    resultado_final,
                    data_conclusao,
                    dados_extras_json,
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
                    data_conclusao,
                    dados_extras
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    aluno_id,
                    id_historico_escolar,
                    resultado_final,
                    data_conclusao,
                    dados_extras_json,
                ),
            )

            historico_id = cursor.lastrowid

        _limpar_disciplinas_antigas(cursor, aluno_id, historico_id)

        for item in base_comum:
            if not item.get("nome"):
                continue

            resultado = item.get("resultado")
            if resultado:
                resultado = str(resultado).strip()[:30]

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
                    _nota_segura(
                        item.get("nota"),
                        item.get("nome") or "Formação Geral Básica",
                    ),
                    item.get("ano_letivo"),
                    resultado,
                    _percentual_seguro(
                        item.get("frequencia_percentual"),
                        item.get("nome") or "Formação Geral Básica",
                    ),
                    item.get("carga_horaria_horas_aula"),
                    item.get("carga_horaria_relogio"),
                    item.get("carga_horaria_total_anual"),
                ),
            )

            disciplina_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO aluno_disciplina_base_comum
                    (aluno_id, disciplina_id)
                VALUES (%s, %s)
                """,
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
                    _percentual_seguro(
                        item.get("frequencia_percentual"),
                        item.get("nome") or "Formação Geral Básica",
                    ),
                    item.get("carga_horaria_horas_aula"),
                ),
            )

        for item in itinerario:
            if not item.get("nome"):
                continue

            resultado = item.get("resultado_final")
            if resultado:
                resultado = str(resultado).strip()[:30]

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
                    _nota_segura(
                        item.get("nota"),
                        item.get("nome") or "Itinerário Formativo",
                    ),
                    resultado,
                    item.get("periodo_letivo"),
                    _percentual_seguro(
                        item.get("frequencia"),
                        item.get("nome") or "Itinerário Formativo",
                    ),
                    item.get("carga_horaria"),
                    item.get("carga_horaria_horas_aula")
                    or item.get("carga_horaria"),
                    item.get("carga_horaria_relogio"),
                ),
            )

            disciplina_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO aluno_disciplina_itinerario
                    (aluno_id, disciplina_id)
                VALUES (%s, %s)
                """,
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
                    _percentual_seguro(
                        item.get("frequencia"),
                        item.get("nome") or "Itinerário Formativo",
                    ),
                    item.get("carga_horaria_horas_aula")
                    or item.get("carga_horaria"),
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
            LEFT JOIN cursos c
                ON c.id = a.curso_id
            LEFT JOIN escolas e
                ON e.id = a.escola_id
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
            ORDER BY d.periodo_letivo, d.id
            """,
            (aluno_id,),
        )

        itinerario_banco = cursor.fetchall()

        extras = {}

        if historico and historico.get("dados_extras"):
            bruto = historico["dados_extras"]

            if isinstance(bruto, str):
                extras = json.loads(bruto)
            elif isinstance(bruto, dict):
                extras = bruto

        # O JSON preserva o campo "Ano" do itinerário oficial, que não existe
        # como coluna na tabela antiga. Usamos essa lista para a exibição.
        itinerario_exibicao = extras.get("itinerario") or _lista_segura(
            itinerario_banco
        )

        historico_seguro = _registro_seguro(historico)

        if historico_seguro:
            historico_seguro.pop("dados_extras", None)

        return {
            "aluno": _registro_seguro(aluno),
            "historico": historico_seguro,
            "base_comum": _lista_segura(base_comum),
            "itinerario": itinerario_exibicao,
            "extras": extras,
        }

    finally:
        cursor.close()
        conexao.close()