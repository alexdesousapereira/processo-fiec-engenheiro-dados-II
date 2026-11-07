-- O agregado "3" e as categorias 1 e 2 não podem entrar na média nem no ranking.
SELECT atividade_codigo, atividade_cnae
FROM {{ ref('vw_transformacao_2025') }}
WHERE atividade_cnae !~ '^3\.[0-9]{2}$'
