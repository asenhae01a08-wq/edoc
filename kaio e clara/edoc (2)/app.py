from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import models

app = Flask(__name__)
app.secret_key ='12345678'

def login_required_profissional(f):
    @wraps(f)  # Essential: Preserves function name and docstrings for Flask's routing
    def decorated_function(*args, **kwargs):
        # 1. Pre-request logic (e.g., check headers, log data)
        if 'nivel' not in session or not session['nivell'] != 'Profissional':
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
        if 'nivel' not in session or not session['nivell'] != 'Aluno':
            return redirect(url_for('login'))
            
        # 2. Execute the actual route controller
        response = f(*args, **kwargs)
        
        # 3. Post-request logic (e.g., modify response, log execution)
        return response
        
    return decorated_function

# @app.route('/adicionar_aluno', methods=['POST'])
# def adicionar_aluno():
#     nome = request.form.get('nome')
#     matricula = request.form.get('matricula')
#     cpf = request.form.get('cpf')
#     email = request.form.get('email')
#     data_nascimento = request.form.get('dataNascimento')

#     # Validações
#     if not all([nome, matricula, cpf, email, data_nascimento]):
#         flash('Todos os campos são obrigatórios!', 'error')
#         return redirect(url_for('index'))   # volta pro index por enquanto

#     if len(cpf) != 14:
#         flash('CPF inválido! Deve ter 14 caracteres (com pontuação).', 'error')
#         return redirect(url_for('index'))

#     try:
#         conectar = conectar_db()
#         cursor = conectar.cursor()

#         cursor.execute("""
#             INSERT INTO aluno (nome, matricula, cpf, email, data_nascimento)
#             VALUES (?, ?, ?, ?, ?)
#         """, (nome, matricula, cpf, email, data_nascimento))

#         conectar.commit()
#         conectar.close()

#         flash('Aluno cadastrado com sucesso!', 'success')
#         return redirect(url_for('index'))

#     except sqlite3.IntegrityError:
#         flash('Matrícula ou CPF já cadastrado!', 'error')
#         return redirect(url_for('index'))
#     except Exception as e:
#         flash(f'Erro ao cadastrar: {str(e)}', 'error')
#         return redirect(url_for('index'))
    
@app.route("/login")
def login():
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

@app.route("/login", methods=['POST'])
def realizarLoigin():
    email = request.form.get("email")
    senha = request.form.get("senha")

    usuario = models.verificarLogin(email, senha)
    if usuario == None:
        redirect(url_for('login'))
    else:
        session['nivel'] = usuario['cargo_nivel']
        session['nome'] = usuario['nome']
        if(session['nivel'] == "Profissional"):
            redirect(url_for('inicialp'))
        else:
            redirect(url_for('iniciala'))