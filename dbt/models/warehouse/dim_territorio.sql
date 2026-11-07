{{ config(unique_key='territorio_codigo') }}

SELECT territorio_codigo, territorio_nome, nivel, path_origem, data_carga
FROM {{ source('stage', 'territorio') }}
