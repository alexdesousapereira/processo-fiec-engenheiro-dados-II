-- Por definição de média, as diferenças de cada UF e mês somam zero.
SELECT uf_codigo, periodo, SUM(diferenca_para_media) AS soma
FROM {{ ref('vw_transformacao_2025') }}
GROUP BY uf_codigo, periodo
HAVING ABS(SUM(diferenca_para_media)) > 0.000001
