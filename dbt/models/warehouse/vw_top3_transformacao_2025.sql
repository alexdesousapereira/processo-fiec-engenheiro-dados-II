{{ config(materialized='view') }}

-- Requisito S2 a partir da tabela analítica: as 3 atividades de maior índice por UF e mês de 2025.
-- O grão é outro (três linhas por UF e mês), por isso fica numa view própria.
-- ROW_NUMBER garante exatamente 3 linhas, e o código desempata.
WITH ranqueada AS (
    SELECT f.territorio_codigo, f.periodo, f.categoria_codigo,
           f.indice_producao, f.media_atividades_uf_mes, f.diferenca_para_media,
           ROW_NUMBER() OVER (
               PARTITION BY f.territorio_codigo, f.periodo
               ORDER BY f.indice_producao DESC, f.categoria_codigo
           ) AS posicao
    FROM {{ ref('fato_producao_fisica_industrial_2025') }} f
)
SELECT r.territorio_codigo AS uf_codigo,
       t.territorio_nome AS uf_nome,
       r.periodo,
       r.categoria_codigo AS atividade_codigo,
       c.categoria_cnae AS atividade_cnae,
       c.categoria_nome AS atividade_nome,
       r.indice_producao,
       r.media_atividades_uf_mes,
       r.diferenca_para_media,
       r.posicao
FROM ranqueada r
JOIN {{ ref('dim_territorio') }} t USING (territorio_codigo)
JOIN {{ ref('dim_categorias') }} c USING (categoria_codigo)
WHERE r.posicao <= 3
