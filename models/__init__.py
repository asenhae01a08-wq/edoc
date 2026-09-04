# USUÁRIO
from models.usuarioBD import verificarLogin
from models.usuarioBD import buscar_aluno

# ALUNOS
from models.alunoBD import buscar_alunos_por_turma
from models.alunoBD import buscar_todos_alunos
from models.alunoBD import buscar_aluno_por_id
from models.alunoBD import buscar_aluno_por_matricula
from models.alunoBD import buscar_aluno_por_email
from models.alunoBD import cadastrar_aluno

# ESCOLA
from models.escolaBD import buscar_escola

# FICHA 19
from models.ficha19BD import salvar_importacao_pdf
from models.ficha19BD import buscar_dados_ficha_por_aluno
from models.ficha19BD import salvar_edicao_ficha19
