#!/bin/sh
# Executado pelo PostgreSQL só na primeira subida, com o volume vazio.
# O schema warehouse não tem tabelas aqui: quem as cria é o dbt.
set -e

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
     -v senha_leitura="$PIM_LEITURA_SENHA" <<'SQL'
-- Banco separado para os metadados do Airflow
CREATE DATABASE airflow;

CREATE SCHEMA controle;
CREATE SCHEMA stage;
CREATE SCHEMA warehouse;

-- Uma linha por mês da fonte. Guia a extração incremental e o reprocessamento.
CREATE TABLE controle.carga_periodo (
    periodo             integer PRIMARY KEY,
    data_fonte          date        NOT NULL,
    hash_conteudo       char(64)    NOT NULL,
    arquivo             text        NOT NULL,
    linhas              integer     NOT NULL,
    linhas_numericas    integer     NOT NULL,
    linhas_uf_numericas integer     NOT NULL,
    completo            boolean     NOT NULL,
    execucao_id         text        NOT NULL,
    ingestao_em         timestamptz NOT NULL,
    carregado_em        timestamptz          -- nulo: ainda precisa chegar ao warehouse
);

-- Última versão de cada arquivo de apoio. Só muda quando o conteúdo muda.
CREATE TABLE controle.carga_recurso (
    recurso       text PRIMARY KEY CHECK (recurso IN ('metadados', 'localidades')),
    hash_conteudo char(64)    NOT NULL,
    arquivo       text        NOT NULL,
    execucao_id   text        NOT NULL,
    ingestao_em   timestamptz NOT NULL
);

-- Uma linha por pedido feito à API de ingestão.
CREATE TABLE controle.execucao_ingestao (
    execucao_id          text PRIMARY KEY,
    tabela               text NOT NULL
        CHECK (tabela IN ('variaveis', 'territorio', 'categoria', 'producao_fisica')),
    modo                 text NOT NULL CHECK (modo IN ('auto', 'completa', 'reprocessar')),
    inicio               integer,
    fim                  integer,
    situacao             text NOT NULL DEFAULT 'pendente'
        CHECK (situacao IN ('pendente', 'executando', 'sucesso', 'falha', 'interrompida')),
    periodos_gravados    integer NOT NULL DEFAULT 0,
    periodos_sem_mudanca integer NOT NULL DEFAULT 0,
    periodos_parciais    integer[] NOT NULL DEFAULT '{}',
    meses_gravados       integer[] NOT NULL DEFAULT '{}',  -- ganharam uma nova versão bruta
    meses_stage          integer[] NOT NULL DEFAULT '{}',  -- foram tratados e carregados na Stage
    linhas_stage         jsonb NOT NULL DEFAULT '{}',
    nulos_stage          jsonb NOT NULL DEFAULT '{}',
    causa_tipo           text,
    causa_mensagem       text,
    criada_em            timestamptz NOT NULL DEFAULT now(),
    iniciada_em          timestamptz,
    concluida_em         timestamptz,
    CHECK ((inicio IS NULL) = (fim IS NULL))
);

-- A expressão constante faz o índice aceitar uma só linha em aberto: é o banco que
-- resolve a corrida entre dois pedidos simultâneos, sem trava na memória da API.
CREATE UNIQUE INDEX execucao_ingestao_uma_em_aberto
    ON controle.execucao_ingestao ((true))
    WHERE situacao IN ('pendente', 'executando');

-- Stage: já tratada, sem chaves. Cada carga esvazia e recarrega as tabelas envolvidas.
CREATE TABLE stage.territorio (
    territorio_codigo integer,
    territorio_nome   text,
    nivel             text,
    path_origem       text,
    data_carga        timestamptz
);

CREATE TABLE stage.variaveis (
    variavel_codigo integer,
    variavel_nome   text,
    unidade         text,
    path_origem     text,
    data_carga      timestamptz
);

CREATE TABLE stage.categoria (
    categoria_codigo           integer,
    categoria_cnae             text,
    categoria_nome             text,
    eh_atividade_transformacao boolean,
    path_origem                text,
    data_carga                 timestamptz
);

CREATE TABLE stage.producao_fisica (
    territorio_codigo integer,
    periodo           integer,
    variavel_codigo   integer,
    categoria_codigo  integer,
    valor             numeric(14,5),
    simbolo_origem    text,
    execucao_id       text,
    path_origem       text,
    data_carga        timestamptz
);

-- Usuário somente leitura para o Power BI: só enxerga o warehouse.
CREATE ROLE pim_leitura LOGIN PASSWORD :'senha_leitura';
GRANT USAGE ON SCHEMA warehouse TO pim_leitura;
ALTER DEFAULT PRIVILEGES IN SCHEMA warehouse GRANT SELECT ON TABLES TO pim_leitura;
SQL
