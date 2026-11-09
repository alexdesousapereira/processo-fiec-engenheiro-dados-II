-- Para o top 3 trazer 3 linhas, toda UF precisa de ao menos 3 atividades em cada mês.
SELECT territorio_codigo, periodo, COUNT(*) AS atividades
FROM {{ ref('fato_producao_fisica_industrial_2025') }}
GROUP BY territorio_codigo, periodo
HAVING COUNT(*) < 3
