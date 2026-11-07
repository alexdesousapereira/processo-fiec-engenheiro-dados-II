-- Reforça a chave primária composta do fato. Grão: território x mês x variável x categoria.
SELECT territorio_codigo, periodo, variavel_codigo, categoria_codigo, COUNT(*) AS linhas
FROM {{ ref('fat_producao_fisica') }}
GROUP BY territorio_codigo, periodo, variavel_codigo, categoria_codigo
HAVING COUNT(*) > 1
