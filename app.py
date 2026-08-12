from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from functools import wraps

import models
from leitor_pdf import extrair_conteudo_pdf
from parcer_siepe import extrair_dados_siepe


app = Flask(__name__)
app.secret_key = "12345678"
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024


def login_required_profissional(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("nivel") != "Profissional":
            return redirect(url_for("login"))
        return f(*args, **kwargs)
 
    return decorated_function


def login_required_aluno(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("nivel") != "Aluno":
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identificacao = request.form.get("identificacao", "").strip()
        senha = request.form.get("senha", "")

        usuario = models.verificarLogin(identificacao, senha)

        if usuario is None:
            flash("Matrícula/e-mail ou senha inválidos.")
            return redirect(url_for("login"))

        session.clear()
        session["nome"] = usuario["nome"]
        session["email"] = usuario.get("email")
        session["nivel"] = usuario["cargo_nivel"]
        session["origem"] = usuario.get("origem")

        if usuario["cargo_nivel"] == "Profissional":
            session["id"] = usuario["id"]
            return redirect(url_for("inicialp"))

        # Login de aluno vindo da tabela alunos
        if usuario.get("origem") == "aluno":
            session["aluno_id"] = usuario["id"]
            return redirect(url_for("iniciala"))

        # Compatibilidade se algum usuário do tipo Aluno existir em usuarios
        aluno = models.buscar_aluno_por_email(usuario.get("email"))
        if aluno is None:
            session.clear()
            flash("O usuário aluno não possui cadastro correspondente na tabela alunos.")
            return redirect(url_for("login"))

        session["aluno_id"] = aluno["id"]
        return redirect(url_for("iniciala"))

    return render_template("login.html")


@app.route("/iniciala")
@login_required_aluno
def iniciala():
    aluno_id = session.get("aluno_id")
    aluno = models.buscar_aluno_por_id(aluno_id)

    if aluno is None:
        session.clear()
        flash("Aluno não encontrado.")
        return redirect(url_for("login"))

    return render_template("iniciala.html", aluno=aluno)


@app.route("/inicialp")
@login_required_profissional
def inicialp():
    return render_template("inicialp.html")


# Mantemos este endpoint porque o inicialp.html já aponta para gerar_fichas.
# Agora ele APENAS abre a tela de importação; não altera todos os alunos.
@app.route("/gerar-fichas")
@login_required_profissional
def gerar_fichas():
    return redirect(url_for("ficha19"))


@app.route("/consultar_documentos")
def consultar():
    return render_template("consultar.html")


@app.route("/turma_TDSA")
def turma_3tdsa():
    alunos = models.buscar_alunos_por_turma("3º TDS A")
    return render_template("turma_TDSA.html", alunos=alunos)

@app.route("/turma_TDSB")
def turma_3tdsb():
    alunos = models.buscar_alunos_por_turma("3º TDS B")
    return render_template("turma_TDSB.html", alunos=alunos)

@app.route("/turma_MKTA")
def turma_3mkta():
    alunos = models.buscar_alunos_por_turma("3º MKT A")
    return render_template("turma_MKTA.html", alunos=alunos)

@app.route("/turma_MKTB")
def turma_3mktb():
    alunos = models.buscar_alunos_por_turma("3º MKT B")
    return render_template("turma_MKTB.html", alunos=alunos)


@app.route("/ficha19")
@login_required_profissional
def ficha19():
    return render_template(
        "ficha19.html",
        dados_ficha=None,
    )


@app.route("/ficha19/importar", methods=["POST"])
@login_required_profissional
def importar_pdf_siepe():
    arquivo = request.files.get("arquivoSiepe")

    if arquivo is None or arquivo.filename == "":
        flash("Selecione um PDF do SIEPE.")
        return redirect(url_for("ficha19"))

    if not arquivo.filename.lower().endswith(".pdf"):
        flash("O arquivo selecionado precisa ser um PDF.")
        return redirect(url_for("ficha19"))

    try:
        conteudo = extrair_conteudo_pdf(arquivo)

        dados = extrair_dados_siepe(
            conteudo["texto"],
            conteudo["tabelas"],
            conteudo.get("paginas"),
        )

        matricula = dados.get("aluno", {}).get("matricula")
        if not matricula:
            flash(
                "O PDF foi lido, mas a matrícula não foi encontrada. "
                "Esse PDF precisa ser ajustado no parser antes de salvar no banco."
            )
            return redirect(url_for("ficha19"))

        aluno_id = models.salvar_importacao_pdf(dados)

        flash("PDF importado. Os dados foram gravados e a Ficha 19 foi criada.")
        return redirect(url_for("telagerar", id_aluno=aluno_id))

    except ValueError as erro:
        flash(str(erro))
        return redirect(url_for("ficha19"))
    except Exception as erro:
        app.logger.exception("Erro durante a importação da Ficha 19")
        flash(f"Erro ao processar o PDF: {erro}")
        return redirect(url_for("ficha19"))


@app.route("/telagerar/<int:id_aluno>")
@login_required_profissional
def telagerar(id_aluno):
    aluno = models.buscar_aluno_por_id(id_aluno)

    if aluno is None:
        flash("Aluno não encontrado.")
        return redirect(url_for("consultar"))

    if not aluno.get("possui_ficha"):
        flash("Esse aluno ainda não possui uma Ficha 19 importada.")
        return redirect(url_for("turma_3tdsa"))

    dados_ficha = models.buscar_dados_ficha_por_aluno(id_aluno)

    return render_template(
        "ficha19.html",
        dados_ficha=dados_ficha,
    )


@app.route("/preenchimento", methods=["GET", "POST"])
@login_required_profissional
def preenchimento():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        matricula = request.form.get("matricula", "").strip()
        cpf = request.form.get("cpf", "").strip()
        email = request.form.get("email", "").strip()
        data_nascimento = request.form.get("data_nascimento", "").strip()
        turma = request.form.get("id_turma", "").strip()

        if not all([nome, matricula, cpf, email, data_nascimento, turma]):
            flash("Preencha todos os campos.", "error")
            return redirect(url_for("preenchimento"))

        sucesso, mensagem, senha_inicial = models.cadastrar_aluno(
            nome,
            matricula,
            cpf,
            email,
            data_nascimento,
            turma,
        )

        if not sucesso:
            flash(mensagem, "error")
            return redirect(url_for("preenchimento"))

        flash(
            f"{mensagem} Senha provisória: {senha_inicial}",
            "success",
        )
        return redirect(url_for("preenchimento"))

    return render_template("preenchimento.html")


@app.route("/esqueci", methods=["GET", "POST"])
def esqueci():
    if request.method == "POST":
        flash(
            "A recuperação automática por e-mail ainda não foi configurada no protótipo."
        )
        return redirect(url_for("esqueci"))

    return render_template("esqueci.html")


@app.route("/suporte")
def suporte():
    return render_template("suporte.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.")
    return redirect(url_for("login"))


@app.route("/")
def index():
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
