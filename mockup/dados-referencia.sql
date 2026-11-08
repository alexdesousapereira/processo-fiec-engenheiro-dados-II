-- Números do mockup: Ceará (uf_codigo 23), janeiro de 2025. Toda tela tira daqui os seus valores,
-- e mockup/conferir_mockup.py executa estas mesmas consultas para conferi-los.
-- Cada consulta termina em ";" e é identificada pelo comentário "-- nome:" logo acima dela.

-- nome: atividades
SELECT atividade_cnae, atividade_nome, indice_producao, diferenca_para_media, media_atividades_uf_mes
FROM warehouse.vw_transformacao_2025
WHERE uf_codigo = 23
  AND periodo = 202501
ORDER BY indice_producao DESC, atividade_codigo;

-- nome: media_mensal
SELECT periodo, AVG(media_atividades_uf_mes) AS media_atividades
FROM warehouse.vw_transformacao_2025
WHERE uf_codigo = 23
GROUP BY periodo
ORDER BY periodo;

-- nome: atualizacao
SELECT MAX(data_carga)::date AS atualizado_em
FROM warehouse.fat_producao_fisica;
