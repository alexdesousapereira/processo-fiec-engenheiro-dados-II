-- A view do top 3 precisa ter exatamente 3 linhas em cada UF e mês de 2025, com posições distintas.
SELECT uf_codigo, periodo, COUNT(*) AS linhas
FROM {{ ref('vw_top3_transformacao_2025') }}
GROUP BY uf_codigo, periodo
HAVING COUNT(*) <> 3 OR COUNT(DISTINCT posicao) <> 3
