{{ config(materialized='table') }}

-- Estrutura analítica exigida (A1 a A5). Grão: UF x mês x atividade da Indústria de Transformação, em 2025.
-- Tabela, e não incremental: a média depende de todas as atividades da UF no mês. Se a fonte revisar um
-- valor para "-", o merge manteria a linha antiga; recriar a tabela a cada carga evita isso, e são poucas
-- linhas (17 UFs x 12 meses x até 24 atividades).
-- O filtro de valor nulo evita que atividades sem dado na UF entrem na média (ADR 0004).
SELECT f.territorio_codigo,
       f.periodo,
       f.categoria_codigo,
       f.valor AS indice_producao,
       AVG(f.valor) OVER w AS media_atividades_uf_mes,
       f.valor - AVG(f.valor) OVER w AS diferenca_para_media,
       f.path_origem,
       f.data_carga
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
