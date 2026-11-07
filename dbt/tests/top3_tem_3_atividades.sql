-- Para o top 3 trazer 3 linhas, toda UF precisa de ao menos 3 atividades em cada mês.
SELECT uf_codigo, periodo, COUNT(*) AS atividades
FROM {{ ref('vw_transformacao_2025') }}
GROUP BY uf_codigo, periodo
HAVING COUNT(*) < 3
