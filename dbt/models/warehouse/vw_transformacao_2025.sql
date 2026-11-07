{{ config(materialized='view') }}

-- Requisitos A1 a A4. Grão: UF x mês x atividade da Indústria de Transformação.
-- O filtro de valor nulo evita que atividades sem dado na UF entrem na média (ADR 0004).
SELECT t.territorio_codigo AS uf_codigo,
       t.territorio_nome AS uf_nome,
       f.periodo,
       c.categoria_codigo AS atividade_codigo,
       c.categoria_cnae AS atividade_cnae,
       c.categoria_nome AS atividade_nome,
       f.valor AS indice_producao,
       AVG(f.valor) OVER w AS media_atividades_uf_mes,
       f.valor - AVG(f.valor) OVER w AS diferenca_para_media
FROM {{ ref('fat_producao_fisica') }} f
JOIN {{ ref('dim_territorio') }} t USING (territorio_codigo)
JOIN {{ ref('dim_categorias') }} c USING (categoria_codigo)
JOIN {{ ref('dim_calendario') }} d USING (periodo)
WHERE f.variavel_codigo = 12606
  AND t.nivel = 'N3'
  AND c.eh_atividade_transformacao
  AND f.valor IS NOT NULL
  AND d.ano = 2025
WINDOW w AS (PARTITION BY f.territorio_codigo, f.periodo)
