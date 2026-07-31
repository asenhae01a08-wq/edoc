from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import models

app = Flask(__name__)
app.secret_key ='12345678'

def login_required_profissional(f):
    @wraps(f)  # Essential: Preserves function name and docstrings for Flask's routing
    def decorated_function(*args, **kwargs):
        # 1. Pre-request logic (e.g., check headers, log data)
        if 'nivel' not in session or session['nivel'] != 'Profissional':
            return redirect(url_for('login'))
            
        # 2. Execute the actual route controller
        response = f(*args, **kwargs)
        
        # 3. Post-request logic (e.g., modify response, log execution)
        return response
        
    return decorated_function


def login_required_aluno(f):
    @wraps(f)  # Essential: Preserves function name and docstrings for Flask's routing
    def decorated_function(*args, **kwargs):
        # 1. Pre-request logic (e.g., check headers, log data)
        if 'nivel' not in session or session['nivel'] != 'Aluno':
            return redirect(url_for('login'))
            
        # 2. Execute the actual route controller
        response = f(*args, **kwargs)
        
        # 3. Post-request logic (e.g., modify response, log execution)
        return response
        
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = models.verificarLogin(email, senha)

        if usuario is None:
            flash("E-mail ou senha inválidos.")
            return redirect(url_for("login"))

        session["nivel"] = usuario["cargo_nivel"]
        session["nome"] = usuario["nome"]

        if session["nivel"] == "Profissional":
            return redirect(url_for("inicialp"))

        return redirect(url_for("iniciala"))

    return render_template("login.html")

@app.route("/loginprofissional")
def loginprofissional():
    return render_template("loginprofissional.html")

@app.route("/iniciala")
@login_required_aluno
def iniciala():
    return render_template("iniciala.html")

@app.route("/inicialp")
@login_required_profissional
def inicialp():
    return render_template("inicialp.html")



@app.route("/preenchimento")
def preenchimento():
    return render_template("preenchimento.html")

@app.route("/esqueci")
def esqueci():
    return render_template("esqueci.html")

@app.route("/suorte")
def suorte():
    return render_template("suorte.html")

@app.route("/", methods=["GET", "POST"])
def login1():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = models.verificarLogin(email, senha)

        if usuario is None:
            flash("E-mail ou senha inválidos.")
            return redirect(url_for("login"))

        session["nivel"] = usuario["cargo_nivel"]
        session["nome"] = usuario["nome"]

        if session["nivel"] == "Profissional":
            return redirect(url_for("inicialp"))

        return redirect(url_for("iniciala"))

    return render_template("login.html")