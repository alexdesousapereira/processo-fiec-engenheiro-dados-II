-- Caso conferido à mão: Ceará, 01/2025, 1.117,38133 / 11 atividades = 101,58012.
-- Se o símbolo "-" virasse zero, a média cairia para 46,56.
SELECT territorio_codigo, media_atividades_uf_mes
FROM {{ ref('fato_producao_fisica_industrial_2025') }}
WHERE territorio_codigo = 23
  AND periodo = 202501
  AND ROUND(media_atividades_uf_mes, 5) <> 101.58012
