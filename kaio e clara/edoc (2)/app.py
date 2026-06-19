from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import re

app = Flask(__name__)
app.secret_key ='12345678'

def conectar_db():
    conectar = sqlite3.connect('aluno.db')
    return conectar

def criar_tabela():
    conectar = conectar_db()
    cursor = conectar.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aluno (
            id INTERGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conectar.commit()
    conectar.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adicionar_aluno', methods=['POST'])
def adicionar_aluno():
    nome = request.form.get('nome')
    matricula = request.form.get('matricula')
    cpf = request.form.get('cpf')
    email = request.form.get('email')
    data_nascimento = request.form.get('dataNascimento')

    # Validações
    if not all([nome, matricula, cpf, email, data_nascimento]):
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('index'))   # volta pro index por enquanto

    if len(cpf) != 14:
        flash('CPF inválido! Deve ter 14 caracteres (com pontuação).', 'error')
        return redirect(url_for('index'))

    try:
        conectar = conectar_db()
        cursor = conectar.cursor()

        cursor.execute("""
            INSERT INTO aluno (nome, matricula, cpf, email, data_nascimento)
            VALUES (?, ?, ?, ?, ?)
        """, (nome, matricula, cpf, email, data_nascimento))

        conectar.commit()
        conectar.close()

        flash('Aluno cadastrado com sucesso!', 'success')
        return redirect(url_for('index'))

    except sqlite3.IntegrityError:
        flash('Matrícula ou CPF já cadastrado!', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Erro ao cadastrar: {str(e)}', 'error')
        return redirect(url_for('index'))