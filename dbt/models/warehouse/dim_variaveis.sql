{{ config(unique_key='variavel_codigo') }}

SELECT variavel_codigo, variavel_nome, unidade, path_origem, data_carga
FROM {{ source('stage', 'variaveis') }}
