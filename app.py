import os

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
from leitor_pdf import extrair_conteudo_pdf
from parcer_siepe import extrair_dados_siepe


app = Flask(__name__)
app.secret_key = "12345678"
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024


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

    # ==========================================
    # SE JÁ ESTIVER LOGADO
    # ==========================================

    if request.method == "GET":

        nivel = session.get("nivel")

        if nivel == "Aluno":

            return redirect(
                url_for("iniciala")
            )

        if nivel == "Profissional":

            return redirect(
                url_for("inicialp")
            )


    # ==========================================
    # LOGIN
    # ==========================================

    if request.method == "POST":

        identificacao = request.form.get(
            "identificacao",
            ""
        ).strip()

        senha = request.form.get(
            "senha",
            ""
        )


        if not identificacao or not senha:

            flash(
                "Preencha a identificação e a senha."
            )

            return redirect(
                url_for("login")
            )


        usuario = models.verificarLogin(
            identificacao,
            senha
        )
        print(usuario)

        if usuario is None:

            flash(
                "Matrícula/e-mail ou senha inválidos."
            )

            return redirect(
                url_for("login")
            )


        # Remove qualquer sessão antiga antes
        # de criar a sessão correta.
        session.clear()


        origem = usuario.get(
            "origem"
        )

        cargo = usuario.get(
            "cargo_nivel"
        )


        # ==================================================
        # ALUNO
        #
        # IMPORTANTE:
        # verificamos a origem ANTES do profissional.
        # ==================================================

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

            # Força explicitamente ALUNO
            session["nivel"] = "Aluno"

            session["origem"] = "aluno"


            return redirect(
                url_for("iniciala")
            )


        # ==================================================
        # PROFISSIONAL
        # ==================================================

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

            # Força explicitamente PROFISSIONAL
            session["nivel"] = (
                "Profissional"
            )

            session["origem"] = (
                origem or "usuario"
            )


            return redirect(
                url_for("inicialp")
            )


        # ==================================================
        # TIPO DE USUÁRIO DESCONHECIDO
        # ==================================================

        session.clear()

        flash(
            "O usuário não possui um nível "
            "de acesso válido."
        )

        return redirect(
            url_for("login")
        )


    return render_template(
        "login.html"
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


    return render_template(
        "iniciala.html",
        aluno=aluno
    )
# ==========================================================
# REDEFINIR SENHA - PRIMEIRO ACESSO
# ==========================================================

# ==========================================================
# ÁREA DO PROFISSIONAL
# ==========================================================

@app.route("/inicialp")
# @login_required_profissional
def inicialp():

    return render_template(
        "inicialp.html"
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

@app.route("/consultar_documentos")
@login_required_profissional
def consultar():

    return render_template(
        "consultar.html"
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
            "Os dados foram gravados no banco "
            "e carregados na Ficha 19."
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
# ESQUECI SENHA
# ==========================================================

@app.route(
    "/esqueci",
    methods=["GET", "POST"]
)
def esqueci():

    if request.method == "POST":

        flash(
            "A recuperação automática "
            "por e-mail ainda não foi "
            "configurada no protótipo."
        )

        return redirect(
            url_for("esqueci")
        )

    return render_template(
        "esqueci.html"
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