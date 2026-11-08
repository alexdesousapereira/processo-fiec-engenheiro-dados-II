{{ config(materialized='view') }}

-- A tabela analítica com os nomes da UF e da atividade, para consultas SQL sem joins.
-- Os cálculos (índice, média e diferença) ficam só na tabela fato_producao_fisica_industrial_2025.
SELECT f.territorio_codigo AS uf_codigo,
       t.territorio_nome AS uf_nome,
       f.periodo,
       f.categoria_codigo AS atividade_codigo,
       c.categoria_cnae AS atividade_cnae,
       c.categoria_nome AS atividade_nome,
       f.indice_producao,
       f.media_atividades_uf_mes,
       f.diferenca_para_media
FROM {{ ref('fato_producao_fisica_industrial_2025') }} f
JOIN {{ ref('dim_territorio') }} t USING (territorio_codigo)
JOIN {{ ref('dim_categorias') }} c USING (categoria_codigo)
