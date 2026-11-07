{{ config(unique_key='categoria_codigo') }}

SELECT categoria_codigo, categoria_cnae, categoria_nome, eh_atividade_transformacao, path_origem, data_carga
FROM {{ source('stage', 'categoria') }}
