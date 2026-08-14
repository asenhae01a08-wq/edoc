USE ficha19;

-- ------------------------------------------------------------
-- 0. CONFERÊNCIA ANTES DA ALTERAÇÃO
-- ------------------------------------------------------------
SELECT id, matricula, nome
FROM alunos
ORDER BY id;

-- ------------------------------------------------------------
-- 1. REMOVER TEMPORARIAMENTE AS FOREIGN KEYS QUE APONTAM
--    DIRETAMENTE PARA alunos.id
-- ------------------------------------------------------------

ALTER TABLE aluno_disciplina_base_comum
    DROP FOREIGN KEY aluno_disciplina_base_comum_ibfk_1;

ALTER TABLE aluno_disciplina_itinerario
    DROP FOREIGN KEY aluno_disciplina_itinerario_ibfk_1;

ALTER TABLE historico_escolar_geral
    DROP FOREIGN KEY historico_escolar_geral_ibfk_1;

-- ------------------------------------------------------------
-- 2. TRANSFORMAR alunos.id EM AUTO_INCREMENT
-- ------------------------------------------------------------

ALTER TABLE alunos
    MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT;

-- ------------------------------------------------------------
-- 3. RECRIAR AS FOREIGN KEYS EXATAMENTE COMO ESTAVAM
-- ------------------------------------------------------------

ALTER TABLE aluno_disciplina_base_comum
    ADD CONSTRAINT aluno_disciplina_base_comum_ibfk_1
    FOREIGN KEY (aluno_id)
    REFERENCES alunos(id);

ALTER TABLE aluno_disciplina_itinerario
    ADD CONSTRAINT aluno_disciplina_itinerario_ibfk_1
    FOREIGN KEY (aluno_id)
    REFERENCES alunos(id);

ALTER TABLE historico_escolar_geral
    ADD CONSTRAINT historico_escolar_geral_ibfk_1
    FOREIGN KEY (aluno_id)
    REFERENCES alunos(id);

-- ------------------------------------------------------------
-- 4. ADICIONAR O JSON USADO PELO ficha19BD.py
-- ------------------------------------------------------------

ALTER TABLE historico_escolar_geral
    ADD COLUMN dados_extras JSON NULL
    AFTER data_conclusao;

-- ------------------------------------------------------------
-- 5. CONFERÊNCIA FINAL
-- ------------------------------------------------------------

SHOW COLUMNS FROM alunos LIKE 'id';

SHOW COLUMNS
FROM historico_escolar_geral
LIKE 'dados_extras';

SELECT
    TABLE_NAME,
    CONSTRAINT_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE()
  AND REFERENCED_TABLE_NAME = 'alunos'
  AND REFERENCED_COLUMN_NAME = 'id'
ORDER BY TABLE_NAME, CONSTRAINT_NAME;