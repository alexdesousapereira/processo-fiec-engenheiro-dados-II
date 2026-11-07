{{ config(materialized='view') }}

-- Requisito S2, pronto para o painel. Fica em uma view própria porque o grão é outro:
-- três linhas por UF e mês. ROW_NUMBER garante exatamente 3, e o código desempata.
WITH ranqueada AS (
    SELECT uf_codigo, uf_nome, periodo, atividade_codigo, atividade_cnae, atividade_nome,
           indice_producao, media_atividades_uf_mes, diferenca_para_media,
           ROW_NUMBER() OVER (
               PARTITION BY uf_codigo, periodo
               ORDER BY indice_producao DESC, atividade_codigo
           ) AS posicao
    FROM {{ ref('vw_transformacao_2025') }}
)
SELECT uf_codigo, uf_nome, periodo, atividade_codigo, atividade_cnae, atividade_nome,
       indice_producao, media_atividades_uf_mes, diferenca_para_media, posicao
FROM ranqueada
WHERE posicao <= 3
