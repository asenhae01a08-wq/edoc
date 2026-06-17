from flask import Flask,render_template
import sqlite3
import  re

app = Flask(__name__)
app.secret_key ='12345678'

def conectar_db():
    conectar = sqlite3.connect('clientes.db')
    return conectar

def criar_tabela():
    conectar = conectar_db()
    cursor = conectar.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
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


@app.route('/adicionar_cliente', methods=['POST'])
def adicionar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']


        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash