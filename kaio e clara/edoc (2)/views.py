from main import app
from flask import render_template

@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/loginaluno")
def loginaluno():
    return render_template("loginaluno.html")

@app.route("/loginprofissional")
def loginprofissional():
    return render_template("loginprofissional.html")

@app.route("/iniciala")
def iniciala():
    return render_template("iniciala.html")

@app.route("/inicialp")
def inicialp():
    return render_template("inicialp.html")

@app.route("/PROFISSIONAL")
def PROFISSIONAL():
    return render_template("PROFISSIONAL.html")

@app.route("/preenchimento")
def preenchimento():
    return render_template("preenchimento.html")

@app.route("/esqueci")
def esqueci():
    return render_template("esqueci.html")

@app.route("/suorte")
def suorte():
    return render_template("suorte.html")

