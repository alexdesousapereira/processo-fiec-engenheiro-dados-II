-- Para cada UF e mês de 2025, as 3 atividades da Indústria de Transformação com maior índice de produção.
-- A regra fica na view warehouse.vw_top3_transformacao_2025 (dbt/models/warehouse/vw_top3_transformacao_2025.sql),
-- que lê a estrutura analítica fato_producao_fisica_industrial_2025: ROW_NUMBER por UF e mês, ordenado pelo
-- índice, com o código da atividade como desempate, garante exatamente 3 linhas.
SELECT uf_nome, periodo, posicao, atividade_cnae, atividade_nome, indice_producao
FROM warehouse.vw_top3_transformacao_2025
ORDER BY uf_nome, periodo, posicao;
