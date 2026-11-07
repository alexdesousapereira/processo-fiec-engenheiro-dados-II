{{ config(
    unique_key=['territorio_codigo', 'periodo', 'variavel_codigo', 'categoria_codigo'],
    post_hook="UPDATE controle.carga_periodo c SET carregado_em = now()
               WHERE c.carregado_em IS NULL
                 AND EXISTS (SELECT 1 FROM stage.producao_fisica s
                             WHERE s.periodo = c.periodo AND s.path_origem = c.arquivo)"
) }}

-- O post_hook roda na transação do fato: um mês só deixa de ser pendente se o fato foi gravado.
-- Ele compara o arquivo, e não só o mês: se a Stage ainda tem a versão anterior de um mês
-- com versão nova pendente, marcar pelo mês esconderia o dado novo para sempre.
-- As chaves estrangeiras exigem que as dimensões sejam carregadas antes:
-- depends_on: {{ ref('dim_territorio') }}
-- depends_on: {{ ref('dim_variaveis') }}
-- depends_on: {{ ref('dim_categorias') }}
-- depends_on: {{ ref('dim_calendario') }}

SELECT territorio_codigo, periodo, variavel_codigo, categoria_codigo,
       valor, simbolo_origem, execucao_id, path_origem, data_carga
FROM {{ source('stage', 'producao_fisica') }}
