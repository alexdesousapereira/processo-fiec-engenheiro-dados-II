-- A fonte tem 17 UFs, e não 27. Cada uma precisa aparecer nos 12 meses de 2025.
SELECT territorio_codigo, COUNT(DISTINCT periodo) AS meses
FROM {{ ref('fato_producao_fisica_industrial_2025') }}
GROUP BY territorio_codigo
HAVING COUNT(DISTINCT periodo) <> 12
UNION ALL
SELECT COUNT(DISTINCT territorio_codigo), -1
FROM {{ ref('fato_producao_fisica_industrial_2025') }}
HAVING COUNT(DISTINCT territorio_codigo) <> 17
