-- Caso conferido à mão: Ceará, 01/2025, 1.117,38133 / 11 atividades = 101,58012.
-- Se o símbolo "-" virasse zero, a média cairia para 46,56.
SELECT uf_codigo, media_atividades_uf_mes
FROM {{ ref('vw_transformacao_2025') }}
WHERE uf_codigo = 23
  AND periodo = 202501
  AND ROUND(media_atividades_uf_mes, 5) <> 101.58012
