-- Requisitos S1 e S2: as 3 atividades com maior índice, para cada UF e mês de 2025.
-- ROW_NUMBER garante exatamente 3 linhas, e o código desempata de forma determinística.
WITH ranqueada AS (
    SELECT uf_nome, periodo, atividade_cnae, atividade_nome, indice_producao,
           ROW_NUMBER() OVER (
               PARTITION BY uf_codigo, periodo
               ORDER BY indice_producao DESC, atividade_codigo
           ) AS posicao
    FROM warehouse.vw_transformacao_2025
)
SELECT uf_nome, periodo, posicao, atividade_cnae, atividade_nome, indice_producao
FROM ranqueada
WHERE posicao <= 3
ORDER BY uf_nome, periodo, posicao;
