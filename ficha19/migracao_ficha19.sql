USE ficha19;

-- ============================================================
-- MIGRAÇÃO PARA IMPORTAR O HISTÓRICO ESCOLAR OFICIAL
-- Pode ser executada mais de uma vez.
-- ============================================================

-- 1) status_ficha19: algumas cópias antigas do banco não possuem a coluna.
SET @tem_status = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'alunos'
      AND COLUMN_NAME = 'status_ficha19'
);

SET @sql_status = IF(
    @tem_status = 0,
    "ALTER TABLE alunos
     ADD COLUMN status_ficha19
     ENUM('Pronta para emissão','Em fabricação')
     DEFAULT 'Em fabricação'
     AFTER senha",
    "SELECT 'alunos.status_ficha19 já existe' AS info"
);

PREPARE stmt_status FROM @sql_status;
EXECUTE stmt_status;
DEALLOCATE PREPARE stmt_status;


-- 2) dados_extras:
-- O documento oficial possui informações que não cabem nas tabelas antigas,
-- como endereço/autorização da escola, resumo anual, trilhas, observações,
-- CH em hora/relógio e data/local. Elas serão preservadas em JSON.
SET @tem_extras = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'historico_escolar_geral'
      AND COLUMN_NAME = 'dados_extras'
);

SET @sql_extras = IF(
    @tem_extras = 0,
    "ALTER TABLE historico_escolar_geral
     ADD COLUMN dados_extras JSON NULL
     AFTER data_conclusao",
    "SELECT 'historico_escolar_geral.dados_extras já existe' AS info"
);

PREPARE stmt_extras FROM @sql_extras;
EXECUTE stmt_extras;
DEALLOCATE PREPARE stmt_extras;


-- Conferência
DESCRIBE alunos;
DESCRIBE historico_escolar_geral;
