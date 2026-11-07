"""Usa o PostgreSQL do Compose. Tudo é desfeito no fim: os dados do ambiente não mudam."""
import os

import psycopg2
import pytest

from pim_pf import banco

pytestmark = pytest.mark.skipif("PIM_DB_HOST" not in os.environ, reason="exige o PostgreSQL do Compose")

INSERIR = (
    "INSERT INTO controle.execucao_ingestao (execucao_id, tabela, modo, situacao) "
    "VALUES (%s, 'variaveis', 'auto', %s)"
)


@pytest.fixture
def cursor():
    conexao = banco.conectar()
    try:
        with conexao.cursor() as cursor:
            # Isola o teste de uma execução real que esteja aberta.
            cursor.execute("DELETE FROM controle.execucao_ingestao WHERE situacao IN ('pendente', 'executando')")
            yield cursor
    finally:
        conexao.rollback()
        conexao.close()


def test_duas_execucoes_em_aberto_violam_o_indice(cursor):
    cursor.execute(INSERIR, ("teste-1", "pendente"))
    with pytest.raises(psycopg2.errors.UniqueViolation):
        cursor.execute(INSERIR, ("teste-2", "executando"))


def test_execucao_concluida_nao_bloqueia_a_proxima(cursor):
    cursor.execute(INSERIR, ("teste-1", "sucesso"))
    cursor.execute(INSERIR, ("teste-2", "falha"))
    cursor.execute(INSERIR, ("teste-3", "pendente"))


def test_inicio_sem_fim_e_recusado_pelo_banco(cursor):
    with pytest.raises(psycopg2.errors.CheckViolation):
        cursor.execute(
            "INSERT INTO controle.execucao_ingestao (execucao_id, tabela, modo, inicio) "
            "VALUES ('teste-1', 'variaveis', 'auto', 202501)"
        )
