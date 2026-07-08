from models.conexaoBD import conectar_mysql
import mysql.connector

def verificarLogin(email, senha):
    conexao = conectar_mysql()
    cursor = conexao.cursor(dictionary=True)
        
    query = """
        SELECT *
        FROM usuarios 
        WHERE email = %s 
          AND senha = %s
          AND status = 'Ativo'
        LIMIT 1
    """
    
    cursor.execute(query, (email,senha))
    usuario = cursor.fetchone()
    
    if not usuario:
        return None

    
    return usuario
