-- Validação do lote: a chave do fato precisa ser única na Stage, antes do merge.
SELECT territorio_codigo, periodo, variavel_codigo, categoria_codigo, COUNT(*) AS linhas
FROM {{ source('stage', 'producao_fisica') }}
GROUP BY territorio_codigo, periodo, variavel_codigo, categoria_codigo
HAVING COUNT(*) > 1
