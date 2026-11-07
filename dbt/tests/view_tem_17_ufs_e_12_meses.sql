-- A fonte tem 17 UFs, e não 27. Cada uma precisa aparecer nos 12 meses de 2025.
SELECT uf_codigo, COUNT(DISTINCT periodo) AS meses
FROM {{ ref('vw_transformacao_2025') }}
GROUP BY uf_codigo
HAVING COUNT(DISTINCT periodo) <> 12
UNION ALL
SELECT COUNT(DISTINCT uf_codigo), -1
FROM {{ ref('vw_transformacao_2025') }}
HAVING COUNT(DISTINCT uf_codigo) <> 17
