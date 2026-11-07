-- Cada ano precisa ter os 12 meses, e o código precisa bater com o ano e o mês.
SELECT ano
FROM {{ ref('dim_calendario') }}
GROUP BY ano
HAVING COUNT(*) <> 12
    OR COUNT(*) FILTER (WHERE periodo = ano * 100 + mes) <> 12
