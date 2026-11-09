{{ config(unique_key='periodo') }}

-- Uma linha por mês, o grão da fonte, com a mesma chave AAAAMM do fato.
-- Cobre anos inteiros, do primeiro ao último ano da Stage. Os nomes dos meses não
-- usam to_char porque o resultado dele depende do idioma configurado no banco.
-- Esta dimensão não vem da fonte, e path_origem deixa isso explícito.
WITH limites AS (
    SELECT MIN(periodo) / 100 AS ano_inicial, MAX(periodo) / 100 AS ano_final
    FROM {{ source('stage', 'producao_fisica') }}
),
meses AS (
    SELECT generate_series(
               make_date(ano_inicial, 1, 1),
               make_date(ano_final, 12, 1),
               interval '1 month'
           )::date AS data
    FROM limites
),
partes AS (
    SELECT data,
           EXTRACT(YEAR FROM data)::integer AS ano,
           EXTRACT(MONTH FROM data)::integer AS mes
    FROM meses
),
nomes AS (
    SELECT *,
           (ARRAY['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto',
                  'setembro', 'outubro', 'novembro', 'dezembro'])[mes] AS mes_nome
    FROM partes
)
SELECT ano * 100 + mes AS periodo,
       data,
       ano,
       mes,
       mes_nome,
       -- Rótulo curto do eixo do gráfico mensal no Power BI: jan, fev, mar...
       left(mes_nome, 3) AS mes_curto,
       (mes + 2) / 3 AS trimestre,
       (mes + 5) / 6 AS semestre,
       'gerado:dbt'::text AS path_origem,
       now() AS data_carga
FROM nomes
