-- O agregado "3" e as categorias 1 e 2 não podem entrar na média nem no ranking.
SELECT f.categoria_codigo, c.categoria_cnae
FROM {{ ref('fato_producao_fisica_industrial_2025') }} f
JOIN {{ ref('dim_categorias') }} c USING (categoria_codigo)
WHERE c.categoria_cnae !~ '^3\.[0-9]{2}$'
