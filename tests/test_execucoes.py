import json

import psycopg2
import pytest
from conftest import CursorFalso

from pim_pf import execucoes


def comando_com(cursor: CursorFalso, trecho: str):
    return next((sql, parametros) for sql, parametros in cursor.comandos if trecho in sql)


def test_criar_grava_como_pendente(banco_falso):
    cursor = banco_falso(CursorFalso())
    execucao_id = execucoes.criar("producao_fisica", "auto", 202501, 202503)
    sql, parametros = comando_com(cursor, "INSERT INTO controle.execucao_ingestao")
    assert parametros == (execucao_id, "producao_fisica", "auto", 202501, 202503)
    assert "pendente" not in parametros  # O padrão da coluna é 'pendente'.


def test_segunda_execucao_em_aberto_informa_qual_esta_rodando(banco_falso):
    class CursorComConflito(CursorFalso):
        def execute(self, sql, parametros=None):
            if "INSERT" in sql:
                raise psycopg2.errors.UniqueViolation("índice")
            super().execute(sql, parametros)

    banco_falso(CursorComConflito({"WHERE situacao IN": [("exec-aberta",)]}))
    with pytest.raises(execucoes.ExecucaoEmAndamento) as erro:
        execucoes.criar("variaveis", "auto", None, None)
    assert erro.value.execucao_id == "exec-aberta"


def test_iniciar_so_vale_para_pendente(banco_falso):
    cursor = banco_falso(CursorFalso())
    execucoes.iniciar("exec")
    sql, _ = comando_com(cursor, "UPDATE")
    assert "situacao = 'executando'" in sql
    assert "situacao = 'pendente'" in sql


def test_concluir_grava_o_resumo(banco_falso):
    cursor = banco_falso(CursorFalso())
    execucoes.concluir("exec", {
        "periodos_gravados": 1, "periodos_sem_mudanca": 2, "periodos_parciais": [202609],
        "meses_gravados": [202501], "meses_stage": [202501, 202502],
        "linhas_stage": {"variaveis": 6}, "nulos_stage": {},
    })
    sql, parametros = comando_com(cursor, "UPDATE")
    assert "situacao = 'sucesso'" in sql
    assert "situacao = 'executando'" in sql
    assert parametros[:5] == (1, 2, [202609], [202501], [202501, 202502])
    assert json.loads(parametros[5]) == {"variaveis": 6}


def test_falhar_grava_a_causa(banco_falso):
    cursor = banco_falso(CursorFalso())
    execucoes.falhar("exec", "dados_invalidos", "símbolo")
    sql, parametros = comando_com(cursor, "UPDATE")
    assert "situacao = 'falha'" in sql
    assert parametros == ("dados_invalidos", "símbolo", "exec")


def test_reinicio_marca_em_aberto_como_interrompida(banco_falso):
    cursor = banco_falso(CursorFalso())
    execucoes.marcar_interrompidas()
    sql, _ = comando_com(cursor, "UPDATE")
    assert "situacao = 'interrompida'" in sql
    assert "situacao IN ('pendente', 'executando')" in sql


def test_consultar_monta_a_causa(banco_falso):
    colunas = (
        "exec", "producao_fisica", "auto", None, None, "falha", 0, 0, [], [202501], [202501, 202502], {}, {},
        "fonte_indisponivel", "fora do ar", None, None, None,
    )
    banco_falso(CursorFalso({"FROM controle.execucao_ingestao": [colunas]}))
    execucao = execucoes.consultar("exec")
    assert execucao["situacao"] == "falha"
    assert execucao["meses_gravados"] == [202501]
    assert execucao["meses_stage"] == [202501, 202502]
    assert execucao["causa"] == {"tipo": "fonte_indisponivel", "mensagem": "fora do ar"}


def test_consultar_inexistente_devolve_none(banco_falso):
    banco_falso(CursorFalso())
    assert execucoes.consultar("nao-existe") is None
