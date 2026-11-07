-- Caso conferido à mão: em Ceará, 01/2025, o top 3 é 3.13 Têxteis, 3.24 Metalurgia e 3.11 Bebidas.
WITH esperado (posicao, atividade_cnae) AS (
    VALUES (1::bigint, '3.13'), (2::bigint, '3.24'), (3::bigint, '3.11')
)
SELECT e.posicao, e.atividade_cnae AS esperada, v.atividade_cnae AS obtida
FROM esperado e
LEFT JOIN {{ ref('vw_top3_transformacao_2025') }} v
       ON v.uf_codigo = 23 AND v.periodo = 202501 AND v.posicao = e.posicao
WHERE v.atividade_cnae IS DISTINCT FROM e.atividade_cnae
