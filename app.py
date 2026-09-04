import os
import smtplib
import pandas as pd
from datetime import date

from email.message import EmailMessage
from html import escape

from dotenv import load_dotenv

from itsdangerous import (
    URLSafeTimedSerializer,
    BadSignature,
    SignatureExpired,
)

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    send_file,
)
from functools import wraps
from werkzeug.utils import secure_filename

import models
from models.conexaoBD import conectar_mysql
from leitor_pdf import extrair_conteudo_pdf
from parcer_siepe import extrair_dados_siepe
from leitor_planilha_siepe import extrair_dados_planilha_siepe


# ==========================================================
# VARIÁVEIS DE AMBIENTE
# ==========================================================

load_dotenv(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        ".env",
    )
)


app = Flask(__name__)
app.secret_key = "12345678"
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024


# ==========================================================
# STATUS DA FICHA 19
# ==========================================================

def definir_status_ficha19(aluno_id, novo_status):
    """
    Atualiza somente o status da Ficha 19 do aluno.

    Valores utilizados pelo eDOC:
    - Em fabricação
    - Pronta para emissão
    """

    status_permitidos = (
        "Em fabricação",
        "Pronta para emissão",
    )

    if novo_status not in status_permitidos:
        raise ValueError("Status da Ficha 19 inválido.")

    conexao = conectar_mysql()

    if conexao is None:
        raise RuntimeError(
            "Não foi possível conectar ao banco de dados."
        )

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            UPDATE alunos
            SET status_ficha19 = %s
            WHERE id = %s
            """,
            (novo_status, aluno_id),
        )

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT id FROM alunos WHERE id = %s LIMIT 1",
                (aluno_id,),
            )

            if cursor.fetchone() is None:
                raise ValueError("Aluno não encontrado.")

        conexao.commit()
        return True

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()


# ==========================================================
# PASTA ONDE AS FICHAS 19 GERADAS EM PDF SERÃO SALVAS
# ==========================================================

PASTA_PDFS_GERADOS = os.path.join(
    app.root_path,
    "pdfs_gerados",
)

os.makedirs(
    PASTA_PDFS_GERADOS,
    exist_ok=True,
)

app.config["PASTA_PDFS_GERADOS"] = PASTA_PDFS_GERADOS


# ==========================================================
# DECORADORES DE LOGIN
# ==========================================================

def login_required_profissional(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        nivel = session.get("nivel")

        # Não está logado
        if not nivel:

            flash(
                "Faça login para acessar esta página."
            )

            return redirect(
                url_for("login")
            )


        # É ALUNO tentando entrar em tela profissional
        if nivel == "Aluno":

            return redirect(
                url_for("iniciala")
            )


        # Qualquer coisa diferente de Profissional
        if nivel != "Profissional":

            session.clear()

            return redirect(
                url_for("login")
            )


        return f(*args, **kwargs)

    return decorated_function



def login_required_aluno(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        nivel = session.get("nivel")

        # Não está logado
        if not nivel:

            flash(
                "Faça login para acessar esta página."
            )

            return redirect(
                url_for("login")
            )


        # É PROFISSIONAL tentando entrar em tela do aluno
        if nivel == "Profissional":

            return redirect(
                url_for("inicialp")
            )


        # Qualquer coisa diferente de Aluno
        if nivel != "Aluno":

            session.clear()

            return redirect(
                url_for("login")
            )


        return f(*args, **kwargs)

    return decorated_function


# ==========================================================
# LOGIN
# ==========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # ======================================================
    # GET - ABRE A TELA DE LOGIN
    # ======================================================

    if request.method == "GET":

        # Se o aluno estiver no processo de primeiro acesso,
        # mantém ele na tela de redefinição.
        if (
            session.get("nivel") == "Aluno"
            and session.get("usuario_id")
        ):

            return redirect(
                url_for("redefinir")
            )


        nivel = session.get("nivel")


        if nivel == "Aluno":

            return redirect(
                url_for("iniciala")
            )


        if nivel == "Profissional":

            return redirect(
                url_for("inicialp")
            )


        return render_template(
            "login.html"
        )


    # ======================================================
    # POST - RECEBE LOGIN
    # ======================================================

    identificacao = request.form.get(
        "identificacao",
        ""
    ).strip()


    senha = request.form.get(
        "senha",
        ""
    )


    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if not identificacao or not senha:

        flash(
            "Preencha a identificação e a senha."
        )

        return redirect(
            url_for("login")
        )


    # ======================================================
    # VERIFICA USUÁRIO NO BANCO
    # ======================================================

    usuario = models.verificarLogin(
        identificacao,
        senha
    )


    print(
        "USUÁRIO ENCONTRADO:",
        usuario
    )


    if usuario is None:

        flash(
            "Matrícula/e-mail ou senha inválidos."
        )

        return redirect(
            url_for("login")
        )


    # ======================================================
    # LIMPA SESSÃO ANTIGA
    # ======================================================

    session.clear()


    origem = usuario.get(
        "origem"
    )


    cargo = usuario.get(
        "cargo_nivel"
    )


    # ======================================================
    # ALUNO
    # ======================================================

    if (
        origem == "aluno"
        or cargo == "Aluno"
    ):

        session["aluno_id"] = (
            usuario["id"]
        )

        session["nome"] = (
            usuario["nome"]
        )

        session["email"] = (
            usuario.get("email")
        )

        session["nivel"] = "Aluno"

        session["origem"] = "aluno"


        # ==================================================
        # PRIMEIRO ACESSO
        #
        # primeiro_login = NULL
        # significa que o aluno ainda não redefiniu
        # a senha provisória.
        # ==================================================

        if usuario.get("primeiro_login") is None:

            session["usuario_id"] = (
                usuario["id"]
            )

            return redirect(
                url_for("redefinir")
            )


        # ==================================================
        # ALUNO JÁ REDEFINIU A SENHA
        # ==================================================

        return redirect(
            url_for("iniciala")
        )


    # ======================================================
    # PROFISSIONAL
    # ======================================================

    if cargo == "Profissional":

        session["id"] = (
            usuario["id"]
        )

        session["nome"] = (
            usuario["nome"]
        )

        session["email"] = (
            usuario.get("email")
        )

        session["nivel"] = (
            "Profissional"
        )

        session["origem"] = (
            origem or "usuario"
        )


        return redirect(
            url_for("inicialp")
        )


    # ======================================================
    # TIPO DE USUÁRIO DESCONHECIDO
    # ======================================================

    session.clear()

    flash(
        "O usuário não possui um nível de acesso válido."
    )

    return redirect(
        url_for("login")
    )
# ==========================================================
# ÁREA DO ALUNO
# ==========================================================

@app.route("/iniciala")
@login_required_aluno
def iniciala():

    aluno_id = session.get("aluno_id")

    if not aluno_id:

        session.clear()

        flash(
            "Sessão do aluno não encontrada."
        )

        return redirect(
            url_for("login")
        )


    aluno = models.buscar_aluno_por_id(
        aluno_id
    )


    if aluno is None:

        session.clear()

        flash(
            "Aluno não encontrado."
        )

        return redirect(
            url_for("login")
        )


    # ======================================================
    # ORGANIZA CURSO E TURMA PARA EXIBIÇÃO
    #
    # Exemplo:
    # 3º TDS A
    #
    # Curso:
    # Técnico em Desenvolvimento de Sistemas
    #
    # Turma:
    # 3º A
    # ======================================================

    turma_original = str(
        aluno.get("id_turma")
        or ""
    ).strip()


    turma_maiuscula = turma_original.upper()


    # ======================================================
    # TDS
    # ======================================================

    if "TDS" in turma_maiuscula:

        aluno["curso_nome"] = (
            "Técnico em Desenvolvimento de Sistemas"
        )

        aluno["id_turma"] = (
            turma_original
            .replace("TDS", "")
            .replace("  ", " ")
            .strip()
        )


    # ======================================================
    # MARKETING
    # ======================================================

    elif "MKT" in turma_maiuscula:

        aluno["curso_nome"] = (
            "Técnico em Marketing"
        )

        aluno["id_turma"] = (
            turma_original
            .replace("MKT", "")
            .replace("  ", " ")
            .strip()
        )


    # ======================================================
    # CASO NÃO TENHA TDS/MKT NA TURMA
    # ======================================================

    else:

        aluno["curso_nome"] = (
            aluno.get("curso_nome")
            or "Não informado"
        )


    return render_template(
        "iniciala.html",
        aluno=aluno
    )
# ==========================================================
# REDEFINIR SENHA - PRIMEIRO ACESSO DO ALUNO
# ==========================================================

@app.route(
    "/redefinir",
    methods=["GET", "POST"]
)
def redefinir():

    # ======================================================
    # SEGURANÇA
    # Só entra aqui quem veio do primeiro acesso
    # ======================================================

    usuario_id = session.get(
        "usuario_id"
    )


    if not usuario_id:

        flash(
            "Faça login para continuar.",
            "erro"
        )

        return redirect(
            url_for("login")
        )


    # ======================================================
    # GET
    # ======================================================

    if request.method == "GET":

        return render_template(
            "redefinir.html"
        )


    # ======================================================
    # RECEBE AS SENHAS
    # ======================================================

    senha = request.form.get(
        "senha",
        ""
    ).strip()


    confirmar_senha = request.form.get(
        "confirmar_senha",
        ""
    ).strip()


    # ======================================================
    # CAMPOS VAZIOS
    # ======================================================

    if not senha or not confirmar_senha:

        flash(
            "Preencha todos os campos.",
            "erro"
        )

        return redirect(
            url_for("redefinir")
        )


    # ======================================================
    # SENHA MÍNIMA
    # ======================================================

    if len(senha) < 6:

        flash(
            "A senha deve possuir pelo menos 6 caracteres.",
            "erro"
        )

        return redirect(
            url_for("redefinir")
        )


    # ======================================================
    # CONFIRMAÇÃO
    # ======================================================

    if senha != confirmar_senha:

        flash(
            "As senhas não coincidem.",
            "erro"
        )

        return redirect(
            url_for("redefinir")
        )


    # ======================================================
    # CONEXÃO
    # ======================================================

    conexao = conectar_mysql()


    if conexao is None:

        flash(
            "Não foi possível conectar ao banco de dados.",
            "erro"
        )

        return redirect(
            url_for("redefinir")
        )


    cursor = conexao.cursor()


    try:

        # ==================================================
        # ATUALIZA A SENHA DO ALUNO
        #
        # primeiro_login é DATE.
        # NULL = nunca redefiniu
        # CURRENT_DATE = data da primeira redefinição
        # ==================================================

        cursor.execute(
            """
            UPDATE alunos

            SET
                senha = %s,
                primeiro_login = CURRENT_DATE()

            WHERE id = %s
            """,
            (
                senha,
                usuario_id
            )
        )


        if cursor.rowcount == 0:

            conexao.rollback()

            flash(
                "Aluno não encontrado.",
                "erro"
            )

            return redirect(
                url_for("redefinir")
            )


        conexao.commit()


    except Exception as erro:

        conexao.rollback()

        print(
            "ERRO AO REDEFINIR SENHA DO ALUNO:",
            erro
        )

        flash(
            "Não foi possível redefinir a senha.",
            "erro"
        )

        return redirect(
            url_for("redefinir")
        )


    finally:

        cursor.close()
        conexao.close()


    # ======================================================
    # FINALIZA A SESSÃO DE PRIMEIRO ACESSO
    # ======================================================

    session.clear()


    flash(
        "Senha redefinida com sucesso! "
        "Entre novamente com sua nova senha.",
        "sucesso"
    )


    return redirect(
        url_for("login")
    )

# ==========================================================
# MEUS DOCUMENTOS - ALUNO
# ==========================================================

@app.route("/meus-documentos")
@login_required_aluno
def meus_documentos_aluno():

    aluno_id = session.get("aluno_id")

    if not aluno_id:
        session.clear()
        flash("Sessão do aluno não encontrada.")
        return redirect(url_for("login"))

    aluno = models.buscar_aluno_por_id(aluno_id)

    if aluno is None:
        session.clear()
        flash("Aluno não encontrado.")
        return redirect(url_for("login"))

    dados_ficha = None

    try:
        dados_ficha = models.buscar_dados_ficha_por_aluno(
            aluno_id
        )
    except Exception:
        dados_ficha = None

    historico = {}

    if dados_ficha:
        historico = dados_ficha.get("historico") or {}

    possui_ficha = bool(historico)

    if possui_ficha:
        aluno_ficha = dados_ficha.get("aluno") or aluno

        status = (
            aluno_ficha.get("status_ficha19")
            or aluno.get("status_ficha19")
            or "Em fabricação"
        )

        if status not in (
            "Em fabricação",
            "Pronta para emissão",
        ):
            status = "Em fabricação"

    else:
        status = "Não informado"

    # ======================================================
    # ÚLTIMA SOLICITAÇÃO DE 2ª VIA DO ALUNO
    # ======================================================

    solicitacao_segunda_via = None

    conexao = conectar_mysql()

    if conexao is not None:

        cursor = conexao.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    id,
                    aluno_id,
                    motivo,
                    observacao,
                    status,
                    data_solicitacao,
                    data_atualizacao
                FROM solicitacoes_segunda_via
                WHERE aluno_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (aluno_id,)
            )

            solicitacao_segunda_via = (
                cursor.fetchone()
            )

        except Exception as erro:

            app.logger.exception(
                "Erro ao buscar solicitação de 2ª via do aluno: %s",
                erro
            )

        finally:

            cursor.close()
            conexao.close()

    tem_solicitacao_aberta = bool(
        solicitacao_segunda_via
        and solicitacao_segunda_via.get("status")
        in ("Pendente", "Em análise")
    )

    return render_template(
        "meus_documentos_aluno.html",
        aluno=aluno,
        status=status,
        possui_ficha=possui_ficha,
        solicitacao_segunda_via=solicitacao_segunda_via,
        tem_solicitacao_aberta=tem_solicitacao_aberta,
    )



# ==========================================================
# SOLICITAR 2ª VIA - ALUNO
# ==========================================================

@app.route("/solicitar-segunda-via", methods=["POST"])
@login_required_aluno
def solicitar_segunda_via():

    aluno_id = session.get("aluno_id")

    if not aluno_id:

        session.clear()

        flash(
            "Sessão do aluno não encontrada."
        )

        return redirect(
            url_for("login")
        )

    motivo = request.form.get(
        "motivo",
        ""
    ).strip()

    observacao = request.form.get(
        "observacao",
        ""
    ).strip()

    if not motivo:

        flash(
            "Selecione o motivo da solicitação."
        )

        return redirect(
            url_for("meus_documentos_aluno")
        )

    conexao = conectar_mysql()

    if conexao is None:

        flash(
            "Não foi possível conectar ao banco de dados."
        )

        return redirect(
            url_for("meus_documentos_aluno")
        )

    cursor = conexao.cursor(
        dictionary=True
    )

    try:

        # Impede nova solicitação enquanto houver
        # uma solicitação em aberto.
        cursor.execute(
            """
            SELECT id
            FROM solicitacoes_segunda_via
            WHERE aluno_id = %s
              AND status IN ('Pendente', 'Em análise')
            LIMIT 1
            """,
            (aluno_id,)
        )

        existente = cursor.fetchone()

        if existente:

            flash(
                "Você já possui uma solicitação "
                "de 2ª via em andamento."
            )

            return redirect(
                url_for("meus_documentos_aluno")
            )

        cursor.execute(
            """
            INSERT INTO solicitacoes_segunda_via
            (
                aluno_id,
                motivo,
                observacao,
                status
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                aluno_id,
                motivo,
                observacao,
                "Pendente"
            )
        )

        conexao.commit()

        flash(
            "Solicitação de 2ª via enviada com sucesso."
        )

    except Exception as erro:

        conexao.rollback()

        app.logger.exception(
            "Erro ao solicitar 2ª via: %s",
            erro
        )

        flash(
            "Não foi possível enviar a solicitação de 2ª via."
        )

    finally:

        cursor.close()
        conexao.close()

    return redirect(
        url_for("meus_documentos_aluno")
    )


# ==========================================================
# ÁREA DO PROFISSIONAL
# ==========================================================

@app.route("/inicialp")
@login_required_profissional
def inicialp():

    alunos = models.buscar_todos_alunos()

    # ============================================
    # TOTAL DE ALUNOS
    # ============================================

    total_alunos = len(alunos)

    # ============================================
    # TOTAL DE TURMAS
    # Conta somente as 4 turmas oficiais do eDOC
    # ============================================

    turmas_oficiais = {
        "3º TDS A",
        "3º TDS B",
        "3º MKT A",
        "3º MKT B"
    }

    turmas_encontradas = set()

    for aluno in alunos:

        turma = str(
            aluno.get("id_turma")
            or ""
        ).strip()

        if turma in turmas_oficiais:

            turmas_encontradas.add(turma)

    total_turmas = len(turmas_encontradas)

    # ============================================
    # FICHAS concluído
    #
    # Conta somente alunos que realmente possuem
    # histórico da Ficha 19 salvo no sistema.
    # ============================================

    total_em_andamento = 0

    for aluno in alunos:

        aluno_id = aluno.get("id")

        if not aluno_id:
            continue

        try:

            dados_ficha = models.buscar_dados_ficha_por_aluno(
                aluno_id
            )

            if (
                dados_ficha
                and dados_ficha.get("historico")
            ):

                total_em_andamento += 1

        except Exception:

            continue

    # ============================================
    # SOLICITAÇÕES DE 2ª VIA
    # ============================================

    total_segunda_via = 0

    conexao = conectar_mysql()

    if conexao is not None:

        cursor = conexao.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM solicitacoes_segunda_via
                WHERE status IN ('Pendente', 'Em análise')
                """
            )

            resultado = cursor.fetchone()

            if resultado:
                total_segunda_via = resultado.get("total") or 0

        except Exception as erro:

            app.logger.exception(
                "Erro ao contar solicitações de 2ª via: %s",
                erro
            )

        finally:

            cursor.close()
            conexao.close()

    # ============================================
    # ABRE A TELA
    # ============================================

    return render_template(
        "inicialp.html",
        total_alunos=total_alunos,
        total_turmas=total_turmas,
        total_em_andamento=total_em_andamento,
        total_segunda_via=total_segunda_via
    )


# ==========================================================
# SOLICITAÇÕES DE 2ª VIA - PROFISSIONAL
# ==========================================================

@app.route("/solicitacoes-segunda-via")
@login_required_profissional
def solicitacoes_segunda_via():

    solicitacoes = []

    conexao = conectar_mysql()

    if conexao is None:
        flash("Não foi possível conectar ao banco de dados.")
        return render_template(
            "solicitacoes_segunda_via.html",
            solicitacoes=solicitacoes
        )

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                s.id,
                s.aluno_id,
                a.nome,
                a.matricula,
                a.id_turma AS turma,
                s.motivo,
                s.observacao,
                s.status,
                s.data_solicitacao,
                s.data_atualizacao
            FROM solicitacoes_segunda_via AS s
            INNER JOIN alunos AS a
                ON a.id = s.aluno_id
            ORDER BY s.data_solicitacao DESC
            """
        )

        solicitacoes = cursor.fetchall() or []

    except Exception as erro:
        app.logger.exception(
            "Erro ao buscar solicitações de 2ª via: %s",
            erro
        )

        flash(
            "Não foi possível carregar as solicitações de 2ª via."
        )

    finally:
        cursor.close()
        conexao.close()

    return render_template(
        "solicitacoes_segunda_via.html",
        solicitacoes=solicitacoes
    )


# ==========================================================
# INICIAR ANÁLISE DA SOLICITAÇÃO DE 2ª VIA
# ==========================================================

@app.route(
    "/solicitacoes-segunda-via/<int:id_solicitacao>/iniciar-analise",
    methods=["POST"]
)
@login_required_profissional
def iniciar_analise_segunda_via(id_solicitacao):

    conexao = conectar_mysql()

    if conexao is None:

        flash(
            "Não foi possível conectar ao banco de dados."
        )

        return redirect(
            url_for("solicitacoes_segunda_via")
        )

    cursor = conexao.cursor(
        dictionary=True
    )

    try:

        # Busca o aluno antes de alterar a solicitação.
        cursor.execute(
            """
            SELECT
                s.id,
                s.aluno_id,
                a.nome,
                a.email
            FROM solicitacoes_segunda_via AS s
            INNER JOIN alunos AS a
                ON a.id = s.aluno_id
            WHERE s.id = %s
            LIMIT 1
            """,
            (id_solicitacao,)
        )

        dados_solicitacao = (
            cursor.fetchone()
        )

        cursor.execute(
            """
            UPDATE solicitacoes_segunda_via
            SET status = 'Em análise'
            WHERE id = %s
              AND status = 'Pendente'
            """,
            (id_solicitacao,)
        )

        alterou_status = (
            cursor.rowcount > 0
        )

        conexao.commit()

        if alterou_status:

            aluno_notificacao = {
                "id": (
                    dados_solicitacao.get("aluno_id")
                    if dados_solicitacao
                    else None
                ),
                "nome": (
                    dados_solicitacao.get("nome")
                    if dados_solicitacao
                    else "Estudante"
                ),
                "email": (
                    dados_solicitacao.get("email")
                    if dados_solicitacao
                    else ""
                ),
            }

            tentar_notificar_aluno_por_email(
                aluno=aluno_notificacao,
                assunto="Sua solicitação de 2ª via está em análise",
                titulo="2ª via em análise",
                mensagem_principal=(
                    "Sua solicitação de 2ª via está sendo analisada."
                ),
                descricao=(
                    "A secretaria iniciou a análise da sua solicitação. "
                    "Você pode acompanhar as próximas atualizações "
                    "pela área Meus documentos do eDOC."
                ),
                texto_botao="Acompanhar solicitação",
                cor_destaque="#d38b12",
            )

            flash(
                "Solicitação colocada em análise."
            )

        else:

            flash(
                "A solicitação não estava pendente "
                "ou não foi encontrada."
            )

    except Exception as erro:

        conexao.rollback()

        app.logger.exception(
            "Erro ao iniciar análise da 2ª via: %s",
            erro
        )

        flash(
            "Não foi possível iniciar a análise."
        )

    finally:

        cursor.close()
        conexao.close()

    return redirect(
        url_for("solicitacoes_segunda_via")
    )


# ==========================================================
# CONCLUIR SOLICITAÇÃO DE 2ª VIA
# ==========================================================

@app.route(
    "/solicitacoes-segunda-via/<int:id_solicitacao>/concluir",
    methods=["POST"]
)
@login_required_profissional
def concluir_segunda_via(id_solicitacao):

    conexao = conectar_mysql()

    if conexao is None:

        flash(
            "Não foi possível conectar ao banco de dados."
        )

        return redirect(
            url_for("solicitacoes_segunda_via")
        )

    cursor = conexao.cursor(
        dictionary=True
    )

    try:

        # Busca o aluno antes de concluir a solicitação.
        cursor.execute(
            """
            SELECT
                s.id,
                s.aluno_id,
                a.nome,
                a.email
            FROM solicitacoes_segunda_via AS s
            INNER JOIN alunos AS a
                ON a.id = s.aluno_id
            WHERE s.id = %s
            LIMIT 1
            """,
            (id_solicitacao,)
        )

        dados_solicitacao = (
            cursor.fetchone()
        )

        cursor.execute(
            """
            UPDATE solicitacoes_segunda_via
            SET status = 'Concluída'
            WHERE id = %s
              AND status = 'Em análise'
            """,
            (id_solicitacao,)
        )

        alterou_status = (
            cursor.rowcount > 0
        )

        conexao.commit()

        if alterou_status:

            aluno_notificacao = {
                "id": (
                    dados_solicitacao.get("aluno_id")
                    if dados_solicitacao
                    else None
                ),
                "nome": (
                    dados_solicitacao.get("nome")
                    if dados_solicitacao
                    else "Estudante"
                ),
                "email": (
                    dados_solicitacao.get("email")
                    if dados_solicitacao
                    else ""
                ),
            }

            tentar_notificar_aluno_por_email(
                aluno=aluno_notificacao,
                assunto="Sua solicitação de 2ª via foi concluída",
                titulo="2ª via concluída",
                mensagem_principal=(
                    "Sua solicitação de 2ª via foi concluída."
                ),
                descricao=(
                    "Acesse o eDOC para consultar o status final "
                    "e acompanhar as informações do documento."
                ),
                texto_botao="Ver no eDOC",
                cor_destaque="#1d8a68",
            )

            flash(
                "Solicitação concluída com sucesso."
            )

        else:

            flash(
                "A solicitação precisa estar em análise "
                "antes de ser concluída."
            )

    except Exception as erro:

        conexao.rollback()

        app.logger.exception(
            "Erro ao concluir solicitação de 2ª via: %s",
            erro
        )

        flash(
            "Não foi possível concluir a solicitação."
        )

    finally:

        cursor.close()
        conexao.close()

    return redirect(
        url_for("solicitacoes_segunda_via")
    )


# ==========================================================
# FICHAS 19 concluído
# ==========================================================

@app.route("/fichas-em-andamento")
@login_required_profissional
def fichas_em_andamento():

    alunos = models.buscar_todos_alunos()

    fichas = []

    for aluno in alunos:

        aluno_id = aluno.get("id")

        if not aluno_id:
            continue

        try:

            dados_ficha = models.buscar_dados_ficha_por_aluno(
                aluno_id
            )

        except Exception:
            continue

        # Só entra na lista quem realmente
        # possui uma Ficha 19 importada.
        if (
            dados_ficha
            and dados_ficha.get("historico")
        ):

            dados_aluno = (
                dados_ficha.get("aluno")
                or aluno
            )

            fichas.append(
                {
                    "id": dados_aluno.get("id")
                    or aluno_id,

                    "nome": dados_aluno.get("nome")
                    or "Aluno",

                    "matricula": dados_aluno.get("matricula")
                    or "-",

                    "turma": dados_aluno.get("id_turma")
                    or "-",

                    "status": "concluído"
                }
            )

    return render_template(
        "fichas_em_andamento.html",
        fichas=fichas
    )


# ==========================================================
# EXCLUIR FICHA 19
# Mantém o cadastro do aluno
# ==========================================================

@app.route(
    "/excluir-ficha19/<int:aluno_id>",
    methods=["POST"]
)
@login_required_profissional
def excluir_ficha19(aluno_id):

    conexao = conectar_mysql()

    if conexao is None:

        flash(
            "Não foi possível conectar ao banco de dados.",
            "erro"
        )

        return redirect(
            url_for("fichas_em_andamento")
        )

    cursor = conexao.cursor(
        dictionary=True
    )

    aluno = None

    try:

        # ==================================================
        # CONFERE SE O ALUNO EXISTE
        # ==================================================

        cursor.execute(
            """
            SELECT
                id,
                nome,
                matricula
            FROM alunos
            WHERE id = %s
            LIMIT 1
            """,
            (aluno_id,)
        )

        aluno = cursor.fetchone()

        if aluno is None:

            flash(
                "Aluno não encontrado.",
                "erro"
            )

            return redirect(
                url_for("fichas_em_andamento")
            )

        # ==================================================
        # BUSCA OS HISTÓRICOS DA FICHA
        # ==================================================

        cursor.execute(
            """
            SELECT id
            FROM historico_escolar_geral
            WHERE aluno_id = %s
            """,
            (aluno_id,)
        )

        historicos = cursor.fetchall() or []

        # ==================================================
        # REMOVE DADOS ANUAIS LIGADOS AO HISTÓRICO
        # ==================================================

        for historico in historicos:

            historico_id = historico["id"]

            cursor.execute(
                """
                DELETE FROM historico_escolar_anual_base_comum
                WHERE historico_geral_id = %s
                """,
                (historico_id,)
            )

            cursor.execute(
                """
                DELETE FROM historico_escolar_anual_itinerario_formativo
                WHERE historico_geral_id = %s
                """,
                (historico_id,)
            )

        # ==================================================
        # GUARDA AS DISCIPLINAS DA BASE COMUM
        # ==================================================

        cursor.execute(
            """
            SELECT disciplina_id
            FROM aluno_disciplina_base_comum
            WHERE aluno_id = %s
            """,
            (aluno_id,)
        )

        ids_base = [
            linha["disciplina_id"]
            for linha in (cursor.fetchall() or [])
        ]

        # ==================================================
        # REMOVE OS VÍNCULOS DA BASE COMUM
        # ==================================================

        cursor.execute(
            """
            DELETE FROM aluno_disciplina_base_comum
            WHERE aluno_id = %s
            """,
            (aluno_id,)
        )

        # ==================================================
        # REMOVE DISCIPLINAS ÓRFÃS DA BASE COMUM
        # ==================================================

        for disciplina_id in ids_base:

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM aluno_disciplina_base_comum
                WHERE disciplina_id = %s
                """,
                (disciplina_id,)
            )

            resultado = cursor.fetchone()

            if (
                resultado
                and resultado["total"] == 0
            ):

                cursor.execute(
                    """
                    DELETE FROM disciplinas_anuais_base_comum
                    WHERE id = %s
                    """,
                    (disciplina_id,)
                )

        # ==================================================
        # GUARDA AS DISCIPLINAS DO ITINERÁRIO
        # ==================================================

        cursor.execute(
            """
            SELECT disciplina_id
            FROM aluno_disciplina_itinerario
            WHERE aluno_id = %s
            """,
            (aluno_id,)
        )

        ids_itinerario = [
            linha["disciplina_id"]
            for linha in (cursor.fetchall() or [])
        ]

        # ==================================================
        # REMOVE OS VÍNCULOS DO ITINERÁRIO
        # ==================================================

        cursor.execute(
            """
            DELETE FROM aluno_disciplina_itinerario
            WHERE aluno_id = %s
            """,
            (aluno_id,)
        )

        # ==================================================
        # REMOVE DISCIPLINAS ÓRFÃS DO ITINERÁRIO
        # ==================================================

        for disciplina_id in ids_itinerario:

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM aluno_disciplina_itinerario
                WHERE disciplina_id = %s
                """,
                (disciplina_id,)
            )

            resultado = cursor.fetchone()

            if (
                resultado
                and resultado["total"] == 0
            ):

                cursor.execute(
                    """
                    DELETE FROM disciplinas_anuais_itinerario_formativo
                    WHERE id = %s
                    """,
                    (disciplina_id,)
                )

        # ==================================================
        # REMOVE O HISTÓRICO GERAL
        # ==================================================

        cursor.execute(
            """
            DELETE FROM historico_escolar_geral
            WHERE aluno_id = %s
            """,
            (aluno_id,)
        )

        # ==================================================
        # RESETA O STATUS DA FICHA
        #
        # O cadastro do estudante continua existindo.
        # ==================================================

        cursor.execute(
            """
            UPDATE alunos
            SET status_ficha19 = 'Em fabricação'
            WHERE id = %s
            """,
            (aluno_id,)
        )

        conexao.commit()

        # ==================================================
        # REMOVE O PDF GERADO, CASO EXISTA
        # ==================================================

        matricula = str(
            aluno.get("matricula")
            or aluno_id
        ).strip()

        nome_arquivo = secure_filename(
            f"ficha19_{matricula}.pdf"
        )

        caminho_pdf = os.path.join(
            app.config["PASTA_PDFS_GERADOS"],
            nome_arquivo
        )

        if os.path.exists(caminho_pdf):

            try:

                os.remove(caminho_pdf)

            except Exception as erro_pdf:

                app.logger.warning(
                    "A Ficha 19 foi removida do banco, "
                    "mas o PDF não pôde ser excluído: %s",
                    erro_pdf
                )

        flash(
            f"Ficha 19 de {aluno['nome']} excluída com sucesso. "
            f"O cadastro do estudante foi mantido.",
            "sucesso"
        )

    except Exception as erro:

        conexao.rollback()

        app.logger.exception(
            "Erro ao excluir Ficha 19 do aluno %s",
            aluno_id
        )

        flash(
            f"Não foi possível excluir a Ficha 19: {erro}",
            "erro"
        )

    finally:

        cursor.close()
        conexao.close()

    return redirect(
        url_for("fichas_em_andamento")
    )


# ==========================================================
# GERAR FICHAS
# ==========================================================

@app.route("/gerar-fichas")
@login_required_profissional
def gerar_fichas():

    return redirect(
        url_for("ficha19")
    )



# ==========================================================
# CONSULTAR DOCUMENTOS - COMPATIBILIDADE TEMPORÁRIA
# Enquanto o cabeçalho antigo ainda possuir url_for("consultar"),
# esta rota apenas redireciona para "Turmas e alunos".
# Depois de corrigir cabecalho_profissional.html, ela pode ser removida.
# ==========================================================

@app.route("/consultar_documentos")
@login_required_profissional
def consultar():

    return redirect(
        url_for("turmas_alunos")
    )


# ==========================================================
# TURMAS E ALUNOS
# ==========================================================

@app.route(
    "/turmas_alunos",
    methods=["GET"]
)
@login_required_profissional
def turmas_alunos():

    # Mantém o termo na URL após uma edição feita
    # a partir da pesquisa ao vivo.
    termo = request.args.get(
        "q",
        ""
    ).strip()

    return render_template(
        "turmas_alunos.html",
        termo=termo
    )


# ==========================================================
# PESQUISA AO VIVO DE ESTUDANTES
# ==========================================================

@app.route(
    "/api/pesquisar-alunos",
    methods=["GET"]
)
@login_required_profissional
def pesquisar_alunos_live():

    termo = request.args.get(
        "q",
        ""
    ).strip()

    # Campo vazio: não retorna alunos.
    if not termo:

        return jsonify(
            {
                "alunos": [],
                "quantidade": 0
            }
        )


    try:

        resultados = (
            models.buscar_alunos_por_pesquisa(
                termo
            )
            or []
        )


        alunos = []


        for resultado in resultados:

            aluno_id = resultado.get(
                "id"
            )


            if not aluno_id:

                continue


            # Busca o cadastro completo para que os botões
            # Ver dados e Editar funcionem na própria pesquisa.
            try:

                aluno = (
                    models.buscar_aluno_por_id(
                        aluno_id
                    )
                    or resultado
                )

            except Exception:

                aluno = resultado


            # Verifica se já existe Ficha 19 para mudar
            # o texto entre "Gerar Ficha" e "Consultar Ficha".
            possui_ficha = bool(
                aluno.get(
                    "possui_ficha",
                    False
                )
            )


            if not possui_ficha:

                try:

                    dados_ficha = (
                        models.buscar_dados_ficha_por_aluno(
                            aluno_id
                        )
                    )


                    possui_ficha = bool(
                        dados_ficha
                        and dados_ficha.get(
                            "historico"
                        )
                    )

                except Exception:

                    possui_ficha = False


            data_nascimento = aluno.get(
                "data_nascimento"
            )


            if data_nascimento is None:

                data_nascimento = ""

            else:

                data_nascimento = str(
                    data_nascimento
                )


            alunos.append(
                {
                    "id": aluno_id,
                    "nome": aluno.get("nome") or "",
                    "matricula": aluno.get("matricula") or "",
                    "turma": aluno.get("id_turma") or "",
                    "email": aluno.get("email") or "",
                    "cpf": aluno.get("cpf") or "",
                    "data_nascimento": data_nascimento,
                    "status_ficha19": (
                        aluno.get("status_ficha19")
                        or "Não informado"
                    ),
                    "possui_ficha": possui_ficha,
                }
            )


        return jsonify(
            {
                "alunos": alunos,
                "quantidade": len(alunos)
            }
        )


    except Exception:

        app.logger.exception(
            "Erro na pesquisa ao vivo de estudantes."
        )


        return jsonify(
            {
                "alunos": [],
                "quantidade": 0,
                "erro": (
                    "Não foi possível realizar "
                    "a pesquisa."
                )
            }
        ), 500

# ==========================================================
# IMPORTAR TURMA POR PLANILHA
# ==========================================================

@app.route("/importar-turma", methods=["GET", "POST"])
@login_required_profissional
def importar_turma():

    if request.method == "POST":

        arquivo = request.files.get("arquivo")


        if not arquivo:

            flash(
                "Selecione uma planilha.",
                "erro"
            )

            return redirect(
                url_for("importar_turma")
            )


        try:

            df = pd.read_excel(
                arquivo
            )


            alunos = df.fillna("").to_dict(
                orient="records"
            )


            # guarda temporariamente na sessão
            session["alunos_importacao"] = alunos


            return render_template(
                "preview_turma.html",
                alunos=alunos
            )


        except Exception as erro:


            flash(
                f"Erro ao ler planilha: {erro}",
                "erro"
            )


            return redirect(
                url_for("importar_turma")
            )


    return render_template(
        "importar_turma.html"
    )



# ==========================================================
# CONFIRMAR IMPORTAÇÃO
# ==========================================================
# ==========================================================
# CONFIRMAR IMPORTAÇÃO
# ==========================================================

@app.route("/confirmar-importacao", methods=["POST"])
@login_required_profissional
def confirmar_importacao():


    alunos = session.get(
        "alunos_importacao",
        []
    )


    print("\n==============================")
    print("ALUNOS RECEBIDOS:")
    print(alunos[:1])
    print("==============================\n")



    if not alunos:

        flash(
            "Nenhum aluno encontrado para importar.",
            "erro"
        )

        return redirect(
            url_for("importar_turma")
        )



    conexao = conectar_mysql()



    if conexao is None:

        flash(
            "Erro ao conectar ao banco.",
            "erro"
        )

        return redirect(
            url_for("importar_turma")
        )



    cursor = conexao.cursor()



    importados = 0



    try:


        for aluno in alunos:



            # ==========================
            # BUSCA AUTOMÁTICA DOS CAMPOS
            # ==========================


            nome = next(
                (
                    valor
                    for chave, valor in aluno.items()
                    if "nome" in chave.lower()
                ),
                None
            )


            matricula = next(
                (
                    valor
                    for chave, valor in aluno.items()
                    if "mat" in chave.lower()
                ),
                None
            )


            cpf = next(
                (
                    valor
                    for chave, valor in aluno.items()
                    if "cpf" in chave.lower()
                ),
                ""
            )


            turma = next(
                (
                    valor
                    for chave, valor in aluno.items()
                    if "turma" in chave.lower()
                ),
                ""
            )



            print(
                "IMPORTANDO:",
                nome,
                matricula,
                turma
            )



            if not nome or not matricula:

                continue



            # ==========================
            # VERIFICA DUPLICIDADE
            # ==========================


            cursor.execute(
                """
                SELECT id
                FROM alunos
                WHERE matricula = %s
                """,
                (
                    str(matricula),
                )
            )


            existe = cursor.fetchone()



            if existe:

                continue



            # ==========================
            # INSERE NO BANCO
            # ==========================


            cursor.execute(
                """
                INSERT INTO alunos
                (
                    nome,
                    matricula,
                    cpf,
                    id_turma
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    nome,
                    str(matricula),
                    cpf,
                    turma
                )
            )



            importados += 1



        conexao.commit()



        session.pop(
            "alunos_importacao",
            None
        )



        flash(
            f"{importados} alunos importados com sucesso!",
            "sucesso"
        )



    except Exception as erro:


        conexao.rollback()


        print(
            "ERRO AO IMPORTAR:",
            erro
        )


        flash(
            f"Erro ao importar: {erro}",
            "erro"
        )



    finally:


        cursor.close()

        conexao.close()



    return redirect(
        url_for("turmas_alunos")
    )
# ==========================================================
# TURMA TDS A
# ==========================================================

TURMAS_EDOC = (
    "3º TDS A",
    "3º TDS B",
    "3º MKT A",
    "3º MKT B",
)


def validar_cpf(cpf):
    """
    Valida CPF pelo cálculo oficial dos dois dígitos verificadores.
    Também bloqueia sequências repetidas como 00000000000 e 88888888888.
    """

    cpf = "".join(
        caractere
        for caractere in str(cpf)
        if caractere.isdigit()
    )

    if len(cpf) != 11:
        return False

    if len(set(cpf)) == 1:
        return False

    soma = sum(
        int(cpf[indice]) * (10 - indice)
        for indice in range(9)
    )

    primeiro = (soma * 10) % 11

    if primeiro == 10:
        primeiro = 0

    if primeiro != int(cpf[9]):
        return False

    soma = sum(
        int(cpf[indice]) * (11 - indice)
        for indice in range(10)
    )

    segundo = (soma * 10) % 11

    if segundo == 10:
        segundo = 0

    if segundo != int(cpf[10]):
        return False

    return True


def rota_da_turma(turma):
    """
    Retorna o endpoint Flask correspondente à turma.
    """

    mapa = {
        "3º TDS A": "turma_3tdsa",
        "3º TDS B": "turma_3tdsb",
        "3º MKT A": "turma_3mkta",
        "3º MKT B": "turma_3mktb",
    }

    return mapa.get(
        turma,
        "turmas_alunos"
    )


def carregar_alunos_turma(turma):
    """
    Busca os alunos da turma e completa os dados necessários
    para os botões Ver dados, Editar cadastro e Consultar Ficha.
    """

    alunos_resumidos = (
        models.buscar_alunos_por_turma(
            turma
        )
        or []
    )

    alunos = []

    for aluno_resumido in alunos_resumidos:

        aluno_id = aluno_resumido.get("id")

        if not aluno_id:
            continue

        try:
            aluno = (
                models.buscar_aluno_por_id(
                    aluno_id
                )
                or aluno_resumido
            )

        except Exception:
            aluno = aluno_resumido

        possui_ficha = False

        try:
            dados_ficha = (
                models.buscar_dados_ficha_por_aluno(
                    aluno_id
                )
            )

            possui_ficha = bool(
                dados_ficha
                and dados_ficha.get("historico")
            )

        except Exception:
            possui_ficha = False

        aluno["possui_ficha"] = possui_ficha

        alunos.append(aluno)

    return alunos

@app.route("/turma_TDSA")
@login_required_profissional
def turma_3tdsa():

    return render_template(
        "turma_TDSA.html",
        alunos=carregar_alunos_turma(
            "3 TDS A"
        )
    )


# ==========================================================
# TURMA TDS B
# ==========================================================
@app.route("/turma_TDSB")
@login_required_profissional
def turma_3tdsb():

    return render_template(
        "turma_TDSB.html",
        alunos=carregar_alunos_turma(
            "3 TDS B"
        )
    )

# ==========================================================
# TURMA MKT A
# ==========================================================

@app.route("/turma_MKTA")
@login_required_profissional
def turma_3mkta():

    return render_template(
        "turma_MKTA.html",
        alunos=carregar_alunos_turma(
            "3 MKT A"
        )
    )


# ==========================================================
# TURMA MKT B
# ==========================================================
@app.route("/turma_MKTB")
@login_required_profissional
def turma_3mktb():

    return render_template(
        "turma_MKTB.html",
        alunos=carregar_alunos_turma(
            "3 MKT B"
        )
    )


# ==========================================================
# EDITAR CADASTRO DO ALUNO
# ==========================================================

@app.route(
    "/editar-aluno/<int:aluno_id>",
    methods=["POST"]
)
@login_required_profissional
def editar_aluno(aluno_id):

    nome = request.form.get(
        "nome",
        ""
    ).strip()

    cpf = request.form.get(
        "cpf",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    data_nascimento = request.form.get(
        "data_nascimento",
        ""
    ).strip()

    turma = request.form.get(
        "id_turma",
        ""
    ).strip()

    turma_origem = request.form.get(
        "turma_origem",
        ""
    ).strip()

    retorno = request.form.get(
        "retorno",
        ""
    ).strip()

    termo_busca = request.form.get(
        "termo_busca",
        ""
    ).strip()

    endpoint_voltar = rota_da_turma(
        turma_origem
    )

    def voltar_para_origem():
        """
        Se a edição foi aberta pela busca em Turmas e alunos,
        volta para a mesma pesquisa. Caso contrário, volta
        para a tela da turma de origem.
        """

        if retorno == "turmas_alunos":

            return redirect(
                url_for(
                    "turmas_alunos",
                    q=termo_busca
                )
            )

        return redirect(
            url_for(
                endpoint_voltar
            )
        )

    # ------------------------------------------------------
    # CAMPOS OBRIGATÓRIOS
    # ------------------------------------------------------

    if not all(
        [
            nome,
            cpf,
            email,
            data_nascimento,
            turma,
        ]
    ):

        flash(
            "Preencha todos os campos do cadastro.",
            "erro"
        )

        return voltar_para_origem()

    # ------------------------------------------------------
    # NOME
    # ------------------------------------------------------

    if len(nome) < 3:

        flash(
            "Informe o nome completo do estudante.",
            "erro"
        )

        return voltar_para_origem()

    # ------------------------------------------------------
    # CPF
    # ------------------------------------------------------

    if not validar_cpf(cpf):

        flash(
            "CPF inválido. Confira os números informados.",
            "erro"
        )

        return voltar_para_origem()

    cpf = "".join(
        caractere
        for caractere in cpf
        if caractere.isdigit()
    )

    # ------------------------------------------------------
    # E-MAIL
    # ------------------------------------------------------

    if (
        "@" not in email
        or "." not in email.split("@")[-1]
    ):

        flash(
            "Informe um e-mail válido.",
            "erro"
        )

        return voltar_para_origem()

    # ------------------------------------------------------
    # DATA DE NASCIMENTO
    # ------------------------------------------------------

    try:
        nascimento = date.fromisoformat(
            data_nascimento
        )

    except ValueError:

        flash(
            "Data de nascimento inválida.",
            "erro"
        )

        return voltar_para_origem()

    if nascimento > date.today():

        flash(
            "A data de nascimento não pode estar no futuro.",
            "erro"
        )

        return voltar_para_origem()

    # ------------------------------------------------------
    # TURMA
    # ------------------------------------------------------

    if turma not in TURMAS_EDOC:

        flash(
            "Turma inválida.",
            "erro"
        )

        return voltar_para_origem()

    conexao = conectar_mysql()

    if conexao is None:

        flash(
            "Não foi possível conectar ao banco de dados.",
            "erro"
        )

        return voltar_para_origem()

    cursor = conexao.cursor(
        dictionary=True
    )

    try:

        # --------------------------------------------------
        # CONFERE SE O ALUNO EXISTE
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                nome,
                id_turma

            FROM alunos

            WHERE id = %s

            LIMIT 1
            """,
            (aluno_id,)
        )

        aluno_atual = cursor.fetchone()

        if aluno_atual is None:

            flash(
                "Aluno não encontrado.",
                "erro"
            )

            return voltar_para_origem()

        # --------------------------------------------------
        # CPF NÃO PODE PERTENCER A OUTRO ALUNO
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT id

            FROM alunos

            WHERE
                REPLACE(
                    REPLACE(
                        REPLACE(
                            cpf,
                            '.',
                            ''
                        ),
                        '-',
                        ''
                    ),
                    ' ',
                    ''
                ) = %s

                AND id <> %s

            LIMIT 1
            """,
            (
                cpf,
                aluno_id,
            )
        )

        if cursor.fetchone():

            flash(
                "Este CPF já está cadastrado para outro aluno.",
                "erro"
            )

            return voltar_para_origem()

        # --------------------------------------------------
        # E-MAIL NÃO PODE PERTENCER A OUTRO ALUNO
        # --------------------------------------------------

        cursor.execute(
            """
            SELECT id

            FROM alunos

            WHERE LOWER(email) = LOWER(%s)
              AND id <> %s

            LIMIT 1
            """,
            (
                email,
                aluno_id,
            )
        )

        if cursor.fetchone():

            flash(
                "Este e-mail já está cadastrado para outro aluno.",
                "erro"
            )

            return voltar_para_origem()

        # --------------------------------------------------
        # SALVA AS ALTERAÇÕES
        # --------------------------------------------------

        cursor.execute(
            """
            UPDATE alunos

            SET
                nome = %s,
                cpf = %s,
                email = %s,
                data_nascimento = %s,
                id_turma = %s

            WHERE id = %s
            """,
            (
                nome,
                cpf,
                email,
                data_nascimento,
                turma,
                aluno_id,
            )
        )

        conexao.commit()

        flash(
            f"Cadastro de {nome} atualizado com sucesso.",
            "sucesso"
        )

    except Exception as erro:

        conexao.rollback()

        app.logger.exception(
            "Erro ao editar o aluno %s",
            aluno_id
        )

        flash(
            "Não foi possível salvar as alterações.",
            "erro"
        )

        return voltar_para_origem()

    finally:

        cursor.close()
        conexao.close()

    # Quando a edição veio da pesquisa integrada,
    # volta para a mesma busca.
    if retorno == "turmas_alunos":

        return redirect(
            url_for(
                "turmas_alunos",
                q=termo_busca
            )
        )

    # Nas telas individuais de turma, mantém o comportamento
    # atual: se a turma foi alterada, abre a nova turma.
    return redirect(
        url_for(
            rota_da_turma(turma)
        )
    )


# ==========================================================
# FICHA 19
#
# /ficha19
# abre vazia
#
# /ficha19?aluno_id=12
# abre preenchida
# ==========================================================

@app.route("/ficha19")
# @login_required_profissional
def ficha19():

    aluno_id = request.args.get(
        "aluno_id",
        type=int
    )

    if aluno_id is None:

        return render_template(
            "ficha19.html",
            dados_ficha=None,
            aluno_id=None
        )

    aluno = models.buscar_aluno_por_id(
        aluno_id
    )

    if aluno is None:

        flash(
            "Aluno não encontrado."
        )

        return redirect(
            url_for("turmas_alunos")
        )

    try:

        dados_ficha = (
            models.buscar_dados_ficha_por_aluno(
                aluno_id
            )
        )

    except Exception as erro:

        app.logger.exception(
            "Erro ao buscar os dados "
            "da Ficha 19"
        )

        flash(
            f"Erro ao buscar a Ficha 19: "
            f"{erro}"
        )

        return redirect(
            url_for("turmas_alunos")
        )

    if not dados_ficha:

        flash(
            "Este aluno ainda não possui "
            "dados de uma Ficha 19 importada."
        )

        return render_template(
            "ficha19.html",
            dados_ficha=None,
            aluno_id=aluno_id
        )

    return render_template(
        "ficha19.html",
        dados_ficha=dados_ficha,
        aluno_id=aluno_id
    )


# ==========================================================
# IMPORTAR PDF DO SIEPE
#
# Modo normal:
# - recebe 1 PDF pelo formulário e mantém o comportamento antigo.
#
# Modo lote:
# - o navegador envia 1 PDF por requisição;
# - o cabeçalho X-EDOC-BATCH=1 faz a rota responder JSON;
# - cada PDF mantém sua própria transação no ficha19BD.py.
# ==========================================================

@app.route(
    "/ficha19/importar",
    methods=["POST"]
)
@login_required_profissional
def importar_pdf_siepe():

    modo_lote = (
        request.headers.get("X-EDOC-BATCH") == "1"
    )

    def responder_erro(
        mensagem,
        status=400
    ):
        if modo_lote:
            return jsonify(
                {
                    "sucesso": False,
                    "erro": str(mensagem),
                }
            ), status

        flash(str(mensagem))

        return redirect(
            url_for("ficha19")
        )

    arquivo = request.files.get(
        "arquivoSiepe"
    )

    if (
        arquivo is None
        or arquivo.filename == ""
    ):
        return responder_erro(
            "Selecione um arquivo do SIEPE.",
            400
        )

    nome_arquivo = (
        arquivo.filename
        or ""
    ).lower()

    if not (
        nome_arquivo.endswith(".pdf")
        or nome_arquivo.endswith(".xlsx")
    ):
        return responder_erro(
            "O arquivo precisa estar no formato PDF ou XLSX.",
            400
        )

    try:

        # ==========================================
        # 1 - IDENTIFICA O TIPO DO ARQUIVO
        # ==========================================

        if nome_arquivo.endswith(".xlsx"):

            # ======================================
            # PLANILHA XLSX
            # ======================================

            dados = (
                extrair_dados_planilha_siepe(
                    arquivo
                )
            )

        else:

            # ======================================
            # PDF DO SIEPE
            # ======================================

            conteudo = extrair_conteudo_pdf(
                arquivo
            )

            dados = extrair_dados_siepe(
                conteudo["texto"],
                conteudo["tabelas"],
                conteudo.get("paginas")
            )

        aluno_pdf = dados.get(
            "aluno",
            {}
        )

        matricula = aluno_pdf.get(
            "matricula"
        )

        app.logger.info(
            "Ficha 19 lida: arquivo=%s, matricula=%s, base_comum=%s, itinerario=%s",
            arquivo.filename,
            matricula,
            len(dados.get("base_comum", [])),
            len(dados.get("itinerario", [])),
        )

        if not matricula:
            return responder_erro(
                "O arquivo foi lido, mas a matrícula não foi encontrada.",
                422
            )

        # ==========================================
        # 3 - SALVA NO BANCO
        # ==========================================

        aluno_id = models.salvar_importacao_pdf(
            dados
        )

        if not aluno_id:
            raise ValueError(
                "O arquivo foi processado, "
                "mas não foi possível obter "
                "o ID do aluno salvo."
            )

        # Ao importar/gerar a Ficha 19, o documento entra
        # automaticamente em processamento.
        definir_status_ficha19(
            aluno_id,
            "Em fabricação"
        )

        # ==========================================
        # 4 - CONFERE O BANCO
        # ==========================================

        dados_salvos = (
            models.buscar_dados_ficha_por_aluno(
                aluno_id
            )
        )

        if not dados_salvos:
            raise ValueError(
                "O PDF foi processado, "
                "mas os dados não puderam "
                "ser recuperados do banco."
            )

        aluno_salvo = (
            dados_salvos.get("aluno")
            or {}
        )

        # ==========================================
        # NOTIFICA O ALUNO - EM FABRICAÇÃO
        # ==========================================

        email_status_enviado = (
            tentar_notificar_aluno_por_email(
                aluno=aluno_salvo,
                assunto="Sua Ficha 19 está em processamento",
                titulo="Ficha 19 em fabricação",
                mensagem_principal=(
                    "Sua Ficha 19 começou a ser processada."
                ),
                descricao=(
                    "A secretaria está analisando e preparando "
                    "o documento. Você pode acompanhar o status "
                    "pela área Meus documentos do eDOC."
                ),
                texto_botao="Acompanhar no eDOC",
                cor_destaque="#d38b12",
            )
        )

        # ==========================================
        # 5A - RESPOSTA PARA IMPORTAÇÃO EM LOTE
        # ==========================================

        if modo_lote:
            return jsonify(
                {
                    "sucesso": True,
                    "arquivo": arquivo.filename,
                    "aluno_id": aluno_id,
                    "matricula": (
                        aluno_salvo.get("matricula")
                        or matricula
                    ),
                    "nome": (
                        aluno_salvo.get("nome")
                        or aluno_pdf.get("nome")
                        or ""
                    ),
                    "url_ficha": url_for(
                        "ficha19",
                        aluno_id=aluno_id
                    ),
                    "email_status_enviado": email_status_enviado,
                }
            )

        # ==========================================
        # 5B - COMPORTAMENTO ANTIGO: 1 PDF
        # ==========================================

        flash(
            "Arquivo importado com sucesso. "
            "A Ficha 19 está em fabricação e o aluno "
            "já pode acompanhar o andamento."
        )

        return redirect(
            url_for(
                "ficha19",
                aluno_id=aluno_id
            )
        )

    except ValueError as erro:
        return responder_erro(
            str(erro),
            422
        )

    except Exception as erro:

        app.logger.exception(
            "Erro durante a importação "
            "da Ficha 19: arquivo=%s",
            getattr(
                arquivo,
                "filename",
                "desconhecido"
            ),
        )

        return responder_erro(
            f"Erro ao processar o arquivo: {erro}",
            500
        )


# ==========================================================
# SALVAR ALTERAÇÕES MANUAIS DA FICHA 19
# ==========================================================

@app.route(
    "/ficha19/salvar-alteracoes/<int:id_aluno>",
    methods=["POST"]
)
@login_required_profissional
def salvar_alteracoes_ficha19(id_aluno):

    aluno = models.buscar_aluno_por_id(
        id_aluno
    )

    if aluno is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "Aluno não encontrado."
        }), 404

    dados = request.get_json(
        silent=True
    ) or {}

    controles = dados.get(
        "controles"
    )

    if not isinstance(controles, list):
        return jsonify({
            "sucesso": False,
            "mensagem": (
                "Os campos da Ficha 19 não foram "
                "recebidos corretamente."
            )
        }), 400

    try:
        resultado = models.salvar_edicao_ficha19(
            id_aluno,
            controles
        )

        return jsonify({
            "sucesso": True,
            "mensagem": (
                "Alterações da Ficha 19 salvas "
                "com sucesso."
            ),
            "total_controles": resultado.get(
                "total_controles",
                len(controles)
            )
        })

    except ValueError as erro:
        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), 400

    except Exception as erro:
        app.logger.exception(
            "Erro ao salvar alterações da Ficha 19 do aluno %s",
            id_aluno
        )

        return jsonify({
            "sucesso": False,
            "mensagem": (
                "Não foi possível salvar as alterações: "
                f"{erro}"
            )
        }), 500


# ==========================================================
# FINALIZAR FICHA 19
# ==========================================================

@app.route(
    "/ficha19/finalizar/<int:id_aluno>",
    methods=["POST"]
)
@login_required_profissional
def finalizar_ficha19(id_aluno):

    aluno = models.buscar_aluno_por_id(id_aluno)

    if aluno is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "Aluno não encontrado."
        }), 404

    try:
        dados_ficha = models.buscar_dados_ficha_por_aluno(
            id_aluno
        )

        if not dados_ficha or not dados_ficha.get("historico"):
            return jsonify({
                "sucesso": False,
                "mensagem": (
                    "Este aluno ainda não possui uma "
                    "Ficha 19 importada para finalizar."
                )
            }), 400

        definir_status_ficha19(
            id_aluno,
            "Pronta para emissão"
        )

        email_status_enviado = (
            tentar_notificar_aluno_por_email(
                aluno=aluno,
                assunto="Sua Ficha 19 está pronta",
                titulo="Documento pronto",
                mensagem_principal=(
                    "Sua Ficha 19 está pronta para emissão."
                ),
                descricao=(
                    "O processamento foi concluído. "
                    "Acesse o eDOC para consultar o status "
                    "e verificar as informações do seu documento."
                ),
                texto_botao="Ver no eDOC",
                cor_destaque="#1d8a68",
            )
        )

        return jsonify({
            "sucesso": True,
            "status": "Pronta para emissão",
            "email_status_enviado": email_status_enviado,
            "mensagem": (
                "Ficha 19 finalizada com sucesso. "
                "O aluno já pode visualizar que o "
                "documento está pronto para emissão."
            )
        })

    except Exception as erro:
        app.logger.exception(
            "Erro ao finalizar a Ficha 19 do aluno %s",
            id_aluno
        )

        return jsonify({
            "sucesso": False,
            "mensagem": f"Não foi possível finalizar: {erro}"
        }), 500


# ==========================================================
# TELAGERAR
# ==========================================================

@app.route(
    "/telagerar/<int:id_aluno>"
)
@login_required_profissional
def telagerar(id_aluno):

    return redirect(
        url_for(
            "ficha19",
            aluno_id=id_aluno
        )
    )


# ==========================================================
# SALVAR FICHA GERADA EM PDF
# ==========================================================

@app.route(
    "/ficha19/salvar-pdf/<int:id_aluno>",
    methods=["POST"]
)
@login_required_profissional
def salvar_pdf_ficha19(id_aluno):

    aluno = models.buscar_aluno_por_id(
        id_aluno
    )

    if aluno is None:

        return jsonify({

            "sucesso": False,

            "mensagem":
                "Aluno não encontrado."

        }), 404

    arquivo_pdf = request.files.get(
        "arquivo_pdf"
    )

    if (
        arquivo_pdf is None
        or arquivo_pdf.filename == ""
    ):

        return jsonify({

            "sucesso": False,

            "mensagem":
                "O arquivo PDF gerado "
                "não foi recebido."

        }), 400

    if not arquivo_pdf.filename.lower().endswith(
        ".pdf"
    ):

        return jsonify({

            "sucesso": False,

            "mensagem":
                "O arquivo recebido "
                "não é um PDF."

        }), 400

    matricula = str(
        aluno.get("matricula")
        or id_aluno
    ).strip()

    nome_arquivo = secure_filename(
        f"ficha19_{matricula}.pdf"
    )

    caminho_pdf = os.path.join(

        app.config[
            "PASTA_PDFS_GERADOS"
        ],

        nome_arquivo
    )

    try:

        arquivo_pdf.save(
            caminho_pdf
        )

    except Exception as erro:

        app.logger.exception(
            "Erro ao salvar o PDF "
            "da Ficha 19"
        )

        return jsonify({

            "sucesso": False,

            "mensagem":
                f"Não foi possível "
                f"salvar o PDF: {erro}"

        }), 500

    return jsonify({

        "sucesso": True,

        "mensagem":
            "Ficha 19 salva em PDF "
            "com sucesso.",

        "nome_arquivo":
            nome_arquivo,

        "download_url":
            url_for(
                "baixar_pdf_ficha19",
                id_aluno=id_aluno
            )
    })


# ==========================================================
# DOWNLOAD DO PDF SALVO
# ==========================================================

@app.route(
    "/ficha19/download/<int:id_aluno>"
)
@login_required_profissional
def baixar_pdf_ficha19(id_aluno):

    aluno = models.buscar_aluno_por_id(
        id_aluno
    )

    if aluno is None:

        flash(
            "Aluno não encontrado."
        )

        return redirect(
            url_for("turmas_alunos")
        )

    matricula = str(
        aluno.get("matricula")
        or id_aluno
    ).strip()

    nome_arquivo = secure_filename(
        f"ficha19_{matricula}.pdf"
    )

    caminho_pdf = os.path.join(

        app.config[
            "PASTA_PDFS_GERADOS"
        ],

        nome_arquivo
    )

    if not os.path.exists(
        caminho_pdf
    ):

        flash(
            "A Ficha 19 deste aluno "
            "ainda não foi salva em PDF."
        )

        return redirect(
            url_for(
                "ficha19",
                aluno_id=id_aluno
            )
        )

    return send_file(

        caminho_pdf,

        as_attachment=True,

        download_name=nome_arquivo,

        mimetype="application/pdf"
    )


# ==========================================================
# CADASTRO / PREENCHIMENTO
# ==========================================================

@app.route(
    "/preenchimento",
    methods=["GET", "POST"]
)
@login_required_profissional
def preenchimento():

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        matricula = request.form.get(
            "matricula",
            ""
        ).strip()

        cpf = request.form.get(
            "cpf",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        data_nascimento = request.form.get(
            "data_nascimento",
            ""
        ).strip()

        turma = request.form.get(
            "id_turma",
            ""
        ).strip()

        if not all(
            [
                nome,
                matricula,
                cpf,
                email,
                data_nascimento,
                turma
            ]
        ):

            flash(
                "Preencha todos os campos.",
                "error"
            )

            return redirect(
                url_for("preenchimento")
            )

        # ==================================================
        # VALIDAÇÃO REAL DO CPF
        # ==================================================

        if not validar_cpf(cpf):

            flash(
                "CPF inválido. Informe um CPF verdadeiro.",
                "error"
            )

            return redirect(
                url_for("preenchimento")
            )

        cpf = "".join(
            caractere
            for caractere in cpf
            if caractere.isdigit()
        )

        (
            sucesso,
            mensagem,
            senha_inicial
        ) = models.cadastrar_aluno(

            nome,

            matricula,

            cpf,

            email,

            data_nascimento,

            turma
        )

        if not sucesso:

            flash(
                mensagem,
                "error"
            )

            return redirect(
                url_for("preenchimento")
            )

        flash(
            f"{mensagem} "
            f"Senha provisória: "
            f"{senha_inicial}",
            "success"
        )

        return redirect(
            url_for("preenchimento")
        )

    return render_template(
        "preenchimento.html"
    )


# ==========================================================
# RECUPERAÇÃO DE SENHA POR E-MAIL
# ==========================================================

TOKEN_RECUPERACAO_SALT = "recuperacao-senha-edoc"
TOKEN_RECUPERACAO_TEMPO = 15 * 60


def gerar_token_recuperacao(aluno_id, email):

    serializer = URLSafeTimedSerializer(
        app.secret_key
    )

    return serializer.dumps(
        {
            "aluno_id": aluno_id,
            "email": email,
            "finalidade": "recuperar_senha",
        },
        salt=TOKEN_RECUPERACAO_SALT,
    )


def ler_token_recuperacao(token):

    serializer = URLSafeTimedSerializer(
        app.secret_key
    )

    dados = serializer.loads(
        token,
        salt=TOKEN_RECUPERACAO_SALT,
        max_age=TOKEN_RECUPERACAO_TEMPO,
    )

    if dados.get("finalidade") != "recuperar_senha":
        raise BadSignature(
            "Token com finalidade inválida."
        )

    return dados


def enviar_email_recuperacao(
    email_destino,
    nome_aluno,
    link_recuperacao,
):

    email_edoc = os.getenv(
        "EMAIL_EDOC",
        ""
    ).strip()

    senha_email_edoc = os.getenv(
        "SENHA_EMAIL_EDOC",
        ""
    ).replace(" ", "").strip()

    if not email_edoc:
        raise RuntimeError(
            "EMAIL_EDOC não foi encontrado no arquivo .env."
        )

    if not senha_email_edoc:
        raise RuntimeError(
            "SENHA_EMAIL_EDOC não foi encontrada no arquivo .env."
        )

    mensagem = EmailMessage()

    mensagem["Subject"] = (
        "eDOC - Recuperação de senha"
    )

    mensagem["From"] = (
        f"eDOC <{email_edoc}>"
    )

    mensagem["To"] = email_destino

    mensagem.set_content(
        f"""
Olá, {nome_aluno}!

Recebemos uma solicitação para redefinir a senha da sua conta no eDOC.

Para criar uma nova senha, acesse o link abaixo:

{link_recuperacao}

Este link é válido por 15 minutos.

Se você não solicitou esta alteração, ignore este e-mail.

eDOC
Sistema de Gestão de Documentos Escolares
"""
    )

    mensagem.add_alternative(
        f"""
<!DOCTYPE html>
<html lang="pt-BR">
<body style="margin:0;padding:30px;background:#f1f4f7;font-family:Arial,Helvetica,sans-serif;">

    <div style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #d8e0e6;border-radius:12px;overflow:hidden;">

        <div style="background:#0c4770;padding:24px;text-align:center;color:#ffffff;">
            <div style="font-size:27px;font-weight:700;">eDOC</div>
            <div style="margin-top:4px;font-size:12px;">Sistema de Gestão de Documentos Escolares</div>
        </div>

        <div style="padding:30px;color:#26333d;">

            <h2 style="margin-top:0;color:#073450;">
                Recuperação de senha
            </h2>

            <p>
                Olá, <strong>{nome_aluno}</strong>!
            </p>

            <p style="line-height:1.6;">
                Recebemos uma solicitação para redefinir a senha da sua conta no eDOC.
            </p>

            <div style="text-align:center;margin:30px 0;">
                <a
                    href="{link_recuperacao}"
                    style="display:inline-block;background:#0c4770;color:#ffffff;padding:13px 24px;border-radius:7px;font-size:14px;font-weight:bold;text-decoration:none;"
                >
                    Redefinir minha senha
                </a>
            </div>

            <p style="font-size:13px;color:#667580;line-height:1.6;">
                Este link é válido por <strong>15 minutos</strong>.
            </p>

            <p style="font-size:13px;color:#667580;line-height:1.6;">
                Se você não solicitou esta alteração, pode ignorar este e-mail.
            </p>

        </div>

    </div>

</body>
</html>
""",
        subtype="html",
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        timeout=20,
    ) as servidor:

        servidor.login(
            email_edoc,
            senha_email_edoc,
        )

        servidor.send_message(
            mensagem
        )


# ==========================================================
# NOTIFICAÇÕES DE STATUS POR E-MAIL
# ==========================================================

def obter_link_edoc(endpoint="meus_documentos_aluno"):
    """
    Monta o link que será enviado ao aluno.

    Em produção, configure no .env:
    URL_EDOC=https://seudominio.com

    Durante os testes locais, se URL_EDOC não existir,
    o Flask utiliza automaticamente o endereço da requisição.
    """

    url_base = os.getenv(
        "URL_EDOC",
        ""
    ).strip().rstrip("/")

    caminho = url_for(
        endpoint
    )

    if url_base:
        return (
            f"{url_base}{caminho}"
        )

    return url_for(
        endpoint,
        _external=True
    )


def enviar_email_notificacao_status(
    email_destino,
    nome_aluno,
    assunto,
    titulo,
    mensagem_principal,
    descricao,
    texto_botao="Acessar meus documentos",
    cor_destaque="#0c4770",
):
    """
    Envia uma notificação visual do eDOC para o Gmail do aluno.

    Esta função utiliza as mesmas credenciais já configuradas
    para a recuperação de senha:
    EMAIL_EDOC
    SENHA_EMAIL_EDOC
    """

    email_destino = str(
        email_destino
        or ""
    ).strip()

    if not email_destino:
        raise ValueError(
            "O aluno não possui e-mail cadastrado."
        )

    email_edoc = os.getenv(
        "EMAIL_EDOC",
        ""
    ).strip()

    senha_email_edoc = os.getenv(
        "SENHA_EMAIL_EDOC",
        ""
    ).replace(" ", "").strip()

    if not email_edoc:
        raise RuntimeError(
            "EMAIL_EDOC não foi encontrado no arquivo .env."
        )

    if not senha_email_edoc:
        raise RuntimeError(
            "SENHA_EMAIL_EDOC não foi encontrada no arquivo .env."
        )

    nome_seguro = escape(
        str(
            nome_aluno
            or "Estudante"
        )
    )

    titulo_seguro = escape(
        str(titulo)
    )

    mensagem_segura = escape(
        str(mensagem_principal)
    )

    descricao_segura = escape(
        str(descricao)
    )

    texto_botao_seguro = escape(
        str(texto_botao)
    )

    link_edoc = obter_link_edoc(
        "meus_documentos_aluno"
    )

    mensagem = EmailMessage()

    mensagem["Subject"] = (
        f"eDOC - {assunto}"
    )

    mensagem["From"] = (
        f"eDOC <{email_edoc}>"
    )

    mensagem["To"] = email_destino

    # ------------------------------------------------------
    # VERSÃO TEXTO
    # ------------------------------------------------------

    mensagem.set_content(
        f"""
Olá, {nome_aluno}!

{titulo}

{mensagem_principal}

{descricao}

Acesse o eDOC para acompanhar:
{link_edoc}

eDOC
Sistema de Gestão de Documentos Escolares
"""
    )

    # ------------------------------------------------------
    # VERSÃO HTML
    # ------------------------------------------------------

    mensagem.add_alternative(
        f"""
<!DOCTYPE html>
<html lang="pt-BR">
<body style="
    margin:0;
    padding:30px;
    background:#f1f4f7;
    font-family:Arial,Helvetica,sans-serif;
">

    <div style="
        max-width:580px;
        margin:0 auto;
        background:#ffffff;
        border:1px solid #d8e0e6;
        border-radius:14px;
        overflow:hidden;
        box-shadow:0 8px 24px rgba(12,71,112,0.08);
    ">

        <div style="
            background:#0c4770;
            padding:24px 28px;
            color:#ffffff;
        ">

            <div style="
                font-size:28px;
                font-weight:700;
                line-height:1;
            ">
                eDOC
            </div>

            <div style="
                margin-top:6px;
                font-size:12px;
                opacity:0.9;
            ">
                Gestão Documental Escolar
            </div>

        </div>


        <div style="
            padding:30px;
            color:#26333d;
        ">

            <p style="
                margin:0 0 18px;
                font-size:14px;
            ">
                Olá, <strong>{nome_seguro}</strong>!
            </p>


            <div style="
                margin-bottom:22px;
                padding:16px 18px;
                background:#f7fafc;
                border-left:4px solid {cor_destaque};
                border-radius:8px;
            ">

                <div style="
                    color:{cor_destaque};
                    font-size:12px;
                    font-weight:700;
                    text-transform:uppercase;
                    letter-spacing:0.4px;
                ">
                    Atualização do documento
                </div>

                <h2 style="
                    margin:7px 0 0;
                    color:#17334d;
                    font-size:20px;
                ">
                    {titulo_seguro}
                </h2>

            </div>


            <p style="
                margin:0 0 10px;
                font-size:15px;
                font-weight:700;
                line-height:1.6;
                color:#26333d;
            ">
                {mensagem_segura}
            </p>


            <p style="
                margin:0;
                font-size:13px;
                line-height:1.7;
                color:#667580;
            ">
                {descricao_segura}
            </p>


            <div style="
                margin:28px 0 12px;
                text-align:center;
            ">

                <a
                    href="{link_edoc}"
                    style="
                        display:inline-block;
                        background:#0c4770;
                        color:#ffffff;
                        padding:13px 22px;
                        border-radius:8px;
                        font-size:13px;
                        font-weight:700;
                        text-decoration:none;
                    "
                >
                    {texto_botao_seguro}
                </a>

            </div>


            <p style="
                margin:22px 0 0;
                font-size:11px;
                line-height:1.6;
                color:#8796a1;
                text-align:center;
            ">
                Esta é uma mensagem automática do eDOC.
                Não é necessário responder este e-mail.
            </p>

        </div>

    </div>

</body>
</html>
""",
        subtype="html",
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        timeout=20,
    ) as servidor:

        servidor.login(
            email_edoc,
            senha_email_edoc,
        )

        servidor.send_message(
            mensagem
        )


def tentar_notificar_aluno_por_email(
    aluno,
    assunto,
    titulo,
    mensagem_principal,
    descricao,
    texto_botao="Acessar meus documentos",
    cor_destaque="#0c4770",
):
    """
    O envio do e-mail nunca deve impedir a atualização do status.

    Se o Gmail estiver sem internet ou houver algum problema
    temporário, o status continua sendo salvo normalmente.
    """

    if not aluno:
        return False

    email_destino = str(
        aluno.get("email")
        or ""
    ).strip()

    if not email_destino:
        app.logger.warning(
            "Notificação não enviada: aluno %s sem e-mail cadastrado.",
            aluno.get("id"),
        )

        return False

    try:

        enviar_email_notificacao_status(
            email_destino=email_destino,
            nome_aluno=aluno.get("nome") or "Estudante",
            assunto=assunto,
            titulo=titulo,
            mensagem_principal=mensagem_principal,
            descricao=descricao,
            texto_botao=texto_botao,
            cor_destaque=cor_destaque,
        )

        app.logger.info(
            "Notificação eDOC enviada para aluno_id=%s email=%s",
            aluno.get("id"),
            email_destino,
        )

        return True

    except Exception as erro:

        app.logger.exception(
            "Não foi possível enviar a notificação eDOC "
            "para aluno_id=%s: %s",
            aluno.get("id"),
            erro,
        )

        return False


# ==========================================================
# ESQUECI MINHA SENHA
# ==========================================================

@app.route(
    "/esqueci",
    methods=["GET", "POST"]
)
def esqueci():

    if request.method == "GET":

        return render_template(
            "esqueci.html"
        )

    email = request.form.get(
        "email",
        ""
    ).strip()

    if not email:

        flash(
            "Digite o seu e-mail.",
            "erro"
        )

        return redirect(
            url_for("esqueci")
        )

    conexao = conectar_mysql()

    if conexao is None:

        flash(
            "Não foi possível acessar o sistema agora.",
            "erro"
        )

        return redirect(
            url_for("esqueci")
        )

    cursor = conexao.cursor(
        dictionary=True
    )

    aluno = None

    try:

        cursor.execute(
            """
            SELECT
                id,
                nome,
                email
            FROM alunos
            WHERE LOWER(email) = LOWER(%s)
            LIMIT 1
            """,
            (email,)
        )

        aluno = cursor.fetchone()

    except Exception as erro:

        app.logger.exception(
            "Erro ao procurar e-mail para recuperação: %s",
            erro,
        )

    finally:

        cursor.close()
        conexao.close()

    # Não informa se o e-mail existe ou não.
    # Isso evita que alguém use esta página para descobrir
    # quais endereços estão cadastrados no sistema.
    if aluno is None:

        flash(
            "Se o e-mail estiver cadastrado, você receberá "
            "as instruções para redefinir sua senha.",
            "sucesso"
        )

        return redirect(
            url_for("esqueci")
        )

    token = gerar_token_recuperacao(
        aluno["id"],
        aluno["email"],
    )

    link_recuperacao = url_for(
        "nova_senha",
        token=token,
        _external=True,
    )

    try:

        enviar_email_recuperacao(
            aluno["email"],
            aluno["nome"],
            link_recuperacao,
        )

        app.logger.info(
            "E-mail de recuperação enviado para aluno_id=%s",
            aluno["id"],
        )

    except Exception as erro:

        app.logger.exception(
            "Erro ao enviar e-mail de recuperação: %s",
            erro,
        )

        flash(
            "Não foi possível enviar o e-mail agora. "
            "Tente novamente em alguns minutos.",
            "erro"
        )

        return redirect(
            url_for("esqueci")
        )

    flash(
        "Pronto! Verifique seu e-mail para continuar "
        "a recuperação da senha.",
        "sucesso"
    )

    return redirect(
        url_for("esqueci")
    )


# ==========================================================
# NOVA SENHA - LINK RECEBIDO POR E-MAIL
# ==========================================================

@app.route(
    "/nova-senha/<token>",
    methods=["GET", "POST"]
)
def nova_senha(token):

    try:

        dados = ler_token_recuperacao(
            token
        )

    except SignatureExpired:

        flash(
            "Esse link expirou. Solicite uma nova recuperação de senha.",
            "erro"
        )

        return redirect(
            url_for("esqueci")
        )

    except BadSignature:

        flash(
            "Esse link de recuperação é inválido.",
            "erro"
        )

        return redirect(
            url_for("esqueci")
        )

    aluno_id = dados.get(
        "aluno_id"
    )

    email = dados.get(
        "email"
    )

    if not aluno_id or not email:

        flash(
            "Link de recuperação inválido.",
            "erro"
        )

        return redirect(
            url_for("esqueci")
        )

    if request.method == "GET":

        return render_template(
            "nova_senha.html",
            token=token,
        )

    senha = request.form.get(
        "senha",
        ""
    ).strip()

    confirmar_senha = request.form.get(
        "confirmar_senha",
        ""
    ).strip()

    if not senha or not confirmar_senha:

        flash(
            "Preencha os dois campos.",
            "erro"
        )

        return redirect(
            url_for(
                "nova_senha",
                token=token,
            )
        )

    if len(senha) < 6:

        flash(
            "A senha deve possuir pelo menos 6 caracteres.",
            "erro"
        )

        return redirect(
            url_for(
                "nova_senha",
                token=token,
            )
        )

    if senha != confirmar_senha:

        flash(
            "As senhas não coincidem.",
            "erro"
        )

        return redirect(
            url_for(
                "nova_senha",
                token=token,
            )
        )

    conexao = conectar_mysql()

    if conexao is None:

        flash(
            "Não foi possível acessar o banco de dados.",
            "erro"
        )

        return redirect(
            url_for(
                "nova_senha",
                token=token,
            )
        )

    cursor = conexao.cursor()

    try:

        cursor.execute(
            """
            UPDATE alunos
            SET senha = %s
            WHERE id = %s
              AND LOWER(email) = LOWER(%s)
            """,
            (
                senha,
                aluno_id,
                email,
            )
        )

        if cursor.rowcount == 0:

            conexao.rollback()

            flash(
                "Não foi possível localizar sua conta.",
                "erro"
            )

            return redirect(
                url_for("esqueci")
            )

        conexao.commit()

    except Exception as erro:

        conexao.rollback()

        app.logger.exception(
            "Erro ao alterar senha pela recuperação: %s",
            erro,
        )

        flash(
            "Não foi possível alterar a senha.",
            "erro"
        )

        return redirect(
            url_for(
                "nova_senha",
                token=token,
            )
        )

    finally:

        cursor.close()
        conexao.close()

    # Evita manter qualquer sessão antiga aberta após a troca.
    session.clear()

    flash(
        "Senha alterada com sucesso! "
        "Você já pode entrar com sua nova senha.",
        "sucesso"
    )

    return redirect(
        url_for("login")
    )


# ==========================================================
# SUPORTE
# ==========================================================

@app.route("/suporte")
def suporte():

    return render_template(
        "suporte.html"
    )


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Você saiu da sua conta."
    )

    return redirect(
        url_for("login")
    )


# ==========================================================
# INÍCIO
# ==========================================================

@app.route("/")
def index():

    return redirect(
        url_for("login")
    )

@app.route("/capa")
def capa():

    escola = {
        "nome": "ESCOLA TÉCNICA ESTADUAL MINISTRO FERNANDO LYRA",
        "endereco": "Rua Vereador João Avelino Sobrinho",
        "complemento": "Loteamento Cidade Alta lote 41 a 43",
        "cidade": "Caruaru",
        "uf": "PE",
        "autorizacao": "Decreto 44.071 de 30/01/2017",
        "data_diario_oficial": "31/01/2017",
        "cadastro_escolar": "26187051"
    }

    aluno = {
        "nome": "NOME DO ALUNO",
        "matricula": "",
        "data_nascimento": "",
        "naturalidade": "",
        "cpf": "",
        "curso": "",
        "turma": ""
    }

    ficha = {
        "classificacao": "",
        "reclassificacao": "",
        "serie": "",
        "serie_progressao": "",
        "disciplinas_progressao": "",
        "ensino_religioso": "NÃO",
        "base_legal_religioso": "",
        "dispensa_educacao_fisica": "NÃO",
        "base_legal_educacao_fisica": "",
        "observacoes": ""
    }

    return render_template(
        "capa.html",
        escola=escola,
        aluno=aluno,
        ficha=ficha
    )
@app.route("/gerarficha")
def gerarficha():

    return render_template(
        "gerarficha.html"
    )

# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)