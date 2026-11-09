-- Números do mockup: Ceará (territorio_codigo 23), janeiro de 2025. Toda tela tira daqui os seus valores,
-- e mockup/conferir_mockup.py executa estas mesmas consultas para conferi-los.
-- Cada consulta termina em ";" e é identificada pelo comentário "-- nome:" logo acima dela.

-- nome: atividades
SELECT c.categoria_cnae AS atividade_cnae, c.categoria_nome AS atividade_nome,
       f.indice_producao, f.diferenca_para_media, f.media_atividades_uf_mes
FROM warehouse.fato_producao_fisica_industrial_2025 f
JOIN warehouse.dim_categorias c USING (categoria_codigo)
WHERE f.territorio_codigo = 23
  AND f.periodo = 202501
ORDER BY f.indice_producao DESC, f.categoria_codigo;

-- nome: media_mensal
SELECT periodo, AVG(media_atividades_uf_mes) AS media_atividades
FROM warehouse.fato_producao_fisica_industrial_2025
WHERE territorio_codigo = 23
GROUP BY periodo
ORDER BY periodo;

-- nome: atualizacao
SELECT MAX(data_carga)::date AS atualizado_em
FROM warehouse.fat_producao_fisica;
