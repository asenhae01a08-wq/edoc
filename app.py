import os
import smtplib

from email.message import EmailMessage

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

        cursor.execute(
            """
            UPDATE solicitacoes_segunda_via
            SET status = 'Em análise'
            WHERE id = %s
              AND status = 'Pendente'
            """,
            (id_solicitacao,)
        )

        conexao.commit()

        if cursor.rowcount > 0:

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

        cursor.execute(
            """
            UPDATE solicitacoes_segunda_via
            SET status = 'Concluída'
            WHERE id = %s
              AND status = 'Em análise'
            """,
            (id_solicitacao,)
        )

        conexao.commit()

        if cursor.rowcount > 0:

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
# GERAR FICHAS
# ==========================================================

@app.route("/gerar-fichas")
@login_required_profissional
def gerar_fichas():

    return redirect(
        url_for("ficha19")
    )


# ==========================================================
# CONSULTAR DOCUMENTOS
# ==========================================================

@app.route("/consultar_documentos", methods=["GET"])
@login_required_profissional
def consultar():

    termo = request.args.get(
        "q",
        ""
    ).strip()

    alunos = []

    pesquisou = False


    if termo:

        pesquisou = True

        alunos = models.buscar_alunos_por_pesquisa(
            termo
        )


    return render_template(
        "consultar.html",
        termo=termo,
        alunos=alunos,
        pesquisou=pesquisou
    )

# ==========================================================
# TURMAS E ALUNOS
# ==========================================================

@app.route("/turmas_alunos")
@login_required_profissional
def turmas_alunos():

    return render_template(
        "turmas_alunos.html"
    )

# ==========================================================
# TURMA TDS A
# ==========================================================

@app.route("/turma_TDSA")
@login_required_profissional
def turma_3tdsa():

    alunos = (
        models.buscar_alunos_por_turma(
            "3º TDS A"
        )
    )

    return render_template(
        "turma_TDSA.html",
        alunos=alunos
    )


# ==========================================================
# TURMA TDS B
# ==========================================================

@app.route("/turma_TDSB")
@login_required_profissional
def turma_3tdsb():

    alunos = (
        models.buscar_alunos_por_turma(
            "3º TDS B"
        )
    )

    return render_template(
        "turma_TDSB.html",
        alunos=alunos
    )


# ==========================================================
# TURMA MKT A
# ==========================================================

@app.route("/turma_MKTA")
@login_required_profissional
def turma_3mkta():

    alunos = (
        models.buscar_alunos_por_turma(
            "3º MKT A"
        )
    )

    return render_template(
        "turma_MKTA.html",
        alunos=alunos
    )


# ==========================================================
# TURMA MKT B
# ==========================================================

@app.route("/turma_MKTB")
@login_required_profissional
def turma_3mktb():

    alunos = (
        models.buscar_alunos_por_turma(
            "3º MKT B"
        )
    )

    return render_template(
        "turma_MKTB.html",
        alunos=alunos
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
            url_for("consultar")
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
            url_for("consultar")
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
            "Selecione um PDF do SIEPE.",
            400
        )

    if not arquivo.filename.lower().endswith(
        ".pdf"
    ):
        return responder_erro(
            "O arquivo selecionado precisa ser um PDF.",
            400
        )

    try:

        # ==========================================
        # 1 - LÊ O PDF
        # ==========================================

        conteudo = extrair_conteudo_pdf(
            arquivo
        )

        # ==========================================
        # 2 - EXTRAI AS INFORMAÇÕES
        # ==========================================

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
                "O PDF foi lido, mas a matrícula não foi encontrada.",
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
                "O PDF foi processado, "
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
                }
            )

        # ==========================================
        # 5B - COMPORTAMENTO ANTIGO: 1 PDF
        # ==========================================

        flash(
            "PDF importado com sucesso. "
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
            f"Erro ao processar o PDF: {erro}",
            500
        )


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

        return jsonify({
            "sucesso": True,
            "status": "Pronta para emissão",
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
            url_for("consultar")
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
    app.run(debug=True)