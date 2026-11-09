-- Por definição de média, as diferenças de cada UF e mês somam zero.
-- Lê a tabela analítica, onde a média e a diferença são calculadas. Assim ela também ganha uma tarefa de teste
-- no Airflow (Cosmos), que roda junto o teste unitário da média.
SELECT territorio_codigo, periodo, SUM(diferenca_para_media) AS soma
FROM {{ ref('fato_producao_fisica_industrial_2025') }}
GROUP BY territorio_codigo, periodo
HAVING ABS(SUM(diferenca_para_media)) > 0.000001
