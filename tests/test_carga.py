import gzip
import json
from datetime import datetime, timezone

import pytest
from conftest import LOCALIDADES, METADADOS, CursorFalso, linha_valor

from pim_pf import carga, extracao, fonte, tratamento

MOMENTO = datetime(2026, 11, 7, tzinfo=timezone.utc)


def gravar(pasta, nome, conteudo) -> str:
    arquivo = pasta / nome
    arquivo.write_bytes(gzip.compress(json.dumps(conteudo).encode()))
    return str(arquivo)


@pytest.fixture
def cursor_com_brutos(tmp_path):
    def criar(linhas=None) -> CursorFalso:
        metadados = gravar(tmp_path, "metadados.gz", METADADOS)
        localidades = gravar(tmp_path, "localidades.gz", LOCALIDADES)
        mes = gravar(tmp_path, "mes.gz", linhas or [linha_valor()])

        class Cursor(CursorFalso):
            def execute(self, sql, parametros=None):
                super().execute(sql, parametros)
                if "FROM controle.carga_recurso" in sql:
                    arquivo = metadados if parametros == ("metadados",) else localidades
                    self._ultimo = [(arquivo,)]

        return Cursor({"FROM controle.carga_periodo": [(202501, mes, "exec-1")]})

    return criar


def test_dimensao_esvazia_e_carrega_so_a_sua_tabela(cursor_com_brutos):
    cursor = cursor_com_brutos()
    linhas = carga.carregar_stage(cursor, "variaveis", MOMENTO)
    assert list(cursor.copias) == ["stage.variaveis"]
    assert "TRUNCATE stage.variaveis" in cursor.sql_executado()
    assert "stage.categoria" not in cursor.sql_executado()
    assert linhas["linhas"] == {"variaveis": 2}


def test_producao_carrega_tambem_as_dimensoes(cursor_com_brutos):
    cursor = cursor_com_brutos()
    carga.carregar_stage(cursor, "producao_fisica", MOMENTO)
    assert set(cursor.copias) == {"stage.variaveis", "stage.categoria", "stage.territorio", "stage.producao_fisica"}


@pytest.mark.parametrize("tabela", ["variaveis", "categoria", "territorio", "producao_fisica"])
def test_toda_linha_informa_origem_e_data_de_carga(cursor_com_brutos, tabela):
    cursor = cursor_com_brutos()
    carga.carregar_stage(cursor, tabela, MOMENTO)
    copia = cursor.copias[f"stage.{tabela}"]
    primeira = copia.splitlines()[0]
    assert ".gz," in primeira
    assert "2026-11-07" in primeira


def test_producao_conta_linhas_e_nulos(cursor_com_brutos):
    cursor = cursor_com_brutos([linha_valor(), linha_valor(valor="-", categoria="56689")])
    resumo = carga.carregar_stage(cursor, "producao_fisica", MOMENTO)
    assert resumo["linhas"]["producao_fisica"] == 2
    assert resumo["nulos"] == {"producao_fisica": 1}
    assert resumo["meses"] == [202501]


def test_dimensao_nao_informa_meses(cursor_com_brutos):
    assert carga.carregar_stage(cursor_com_brutos(), "variaveis", MOMENTO)["meses"] == []


def test_log_identifica_os_meses_da_stage(cursor_com_brutos, caplog):
    with caplog.at_level("INFO"):
        carga.carregar_stage(cursor_com_brutos(), "producao_fisica", MOMENTO)
    assert "202501" in caplog.text


def test_dado_invalido_impede_qualquer_copia(cursor_com_brutos):
    cursor = cursor_com_brutos([linha_valor(valor="abc")])
    with pytest.raises(tratamento.DadosInvalidos):
        carga.carregar_stage(cursor, "producao_fisica", MOMENTO)
    assert cursor.copias == {}
    assert "TRUNCATE" not in cursor.sql_executado()


def test_producao_sem_mes_pendente_esvazia_a_stage_de_producao(tmp_path):
    # Sem isso, o dbt regravaria no warehouse os meses da carga anterior.
    metadados = gravar(tmp_path, "metadados.gz", METADADOS)
    localidades = gravar(tmp_path, "localidades.gz", LOCALIDADES)

    class Cursor(CursorFalso):
        def execute(self, sql, parametros=None):
            super().execute(sql, parametros)
            if "FROM controle.carga_recurso" in sql:
                self._ultimo = [(metadados if parametros == ("metadados",) else localidades,)]

    cursor = Cursor()
    resumo = carga.carregar_stage(cursor, "producao_fisica", MOMENTO)
    assert "TRUNCATE stage.producao_fisica" in cursor.sql_executado()
    assert "stage.producao_fisica" not in cursor.copias
    assert resumo["linhas"]["producao_fisica"] == 0


def test_reprocessar_nao_acessa_a_fonte(banco_falso, tmp_path, monkeypatch):
    monkeypatch.setattr(fonte, "criar_sessao", lambda: pytest.fail("acessou a fonte"))
    metadados = gravar(tmp_path, "metadados.gz", METADADOS)
    localidades = gravar(tmp_path, "localidades.gz", LOCALIDADES)
    mes = gravar(tmp_path, "mes.gz", [linha_valor()])

    class Cursor(CursorFalso):
        def execute(self, sql, parametros=None):
            super().execute(sql, parametros)
            if "FROM controle.carga_recurso" in sql:
                self._ultimo = [(metadados if parametros == ("metadados",) else localidades,)]
            elif "SELECT periodo, data_fonte" in sql:
                self._ultimo = [(202501, None, "h", None, True, mes)]
            elif "SELECT periodo, arquivo, execucao_id" in sql:
                self._ultimo = [(202501, mes, "exec-1")]
            elif "SELECT periodo FROM controle.carga_periodo WHERE NOT completo" in sql:
                self._ultimo = []

    banco_falso(Cursor())
    monkeypatch.setattr(extracao, "validar_brutos", lambda cursor: None)
    resumo = carga.executar_extracao("producao_fisica", "reprocessar", None, None, "exec-2")
    assert resumo["linhas_stage"]["producao_fisica"] == 1
    assert resumo["periodos_gravados"] == 0
    assert resumo["meses_gravados"] == []
    assert resumo["meses_stage"] == [202501]
