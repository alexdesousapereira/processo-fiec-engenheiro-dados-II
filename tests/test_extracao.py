import gzip
import json
from datetime import date, datetime
from pathlib import Path

import pytest
from conftest import METADADOS, ConexaoFalsa, CursorFalso, SessaoFalsa, linha_valor

from pim_pf import extracao, fonte

D1, D2 = date(2026, 11, 5), date(2026, 12, 5)
HASH_A = extracao.calcular_hash(b"[]")


def test_sem_mudanca_nao_ha_novidade():
    assert extracao.periodos_com_novidade({202501: D1}, {202501: D1}) == []


def test_mes_novo_e_data_alterada_sao_novidade():
    assert extracao.periodos_com_novidade({202501: D2, 202502: D2}, {202501: D1}) == [202501, 202502]


def test_extracao_interrompida_ainda_aparece_como_novidade():
    # Parte dos meses já tem a data nova; os demais continuam pendentes.
    assert extracao.periodos_com_novidade({202501: D2, 202502: D2}, {202501: D2, 202502: D1}) == [202502]


def test_hash_muda_com_o_conteudo():
    assert extracao.calcular_hash(b"a") == extracao.calcular_hash(b"a")
    assert extracao.calcular_hash(b"a") != extracao.calcular_hash(b"b")


def test_mes_sem_numeros_nas_ufs_fica_parcial():
    # Caso medido em 202609: só o Brasil tem números.
    resumo = extracao.resumir_conteudo([linha_valor(nivel="1", valor="1.0"), linha_valor(nivel="3", valor="...")])
    assert resumo == {"linhas": 2, "linhas_numericas": 1, "linhas_uf_numericas": 0, "completo": False}


def test_caminho_separa_mes_e_versao():
    caminho = extracao.caminho_ingestao(Path("raw"), 202501, datetime(2026, 11, 7, 10, 30, 0))
    assert caminho.as_posix() == "raw/sidra/tabela=8888/periodo=202501/ingestao=20261107T103000"


def test_caminho_do_recurso():
    caminho = extracao.caminho_recurso(Path("raw"), "metadados", datetime(2026, 11, 7, 10, 30, 0))
    assert caminho.as_posix() == "raw/sidra/tabela=8888/metadados/ingestao=20261107T103000"


def test_arquivo_bruto_preserva_o_conteudo_original(tmp_path):
    arquivo = extracao.gravar_bruto(tmp_path / "v1", b'[{"V":"-"}]', {"periodo": 202501})
    assert gzip.decompress(arquivo.read_bytes()) == b'[{"V":"-"}]'
    assert (tmp_path / "v1" / "manifesto.json").exists()


def mes_com(*variaveis, territorio="23"):
    return [linha_valor(uf=territorio, variavel=v, categoria="129320") for v in variaveis]


METADADOS_MINIMOS = {
    "variaveis": [{"id": 12606}, {"id": 11602}],
    "classificacoes": [{"categorias": [{"id": 129320}]}],
}
LOCALIDADES_MINIMAS = {"N3": [{"id": "23"}]}


def test_mes_completo_passa_na_checagem():
    assert extracao.checar_mes(mes_com("12606", "11602"), METADADOS_MINIMOS, LOCALIDADES_MINIMAS) == []


def test_linha_faltando_reprova_o_mes():
    linhas = [*mes_com("12606", "11602"), *mes_com("12606", territorio="35")]
    localidades = {"N3": [{"id": "23"}, {"id": "35"}]}
    assert "3 linhas recebidas, 4 esperadas" in extracao.checar_mes(linhas, METADADOS_MINIMOS, localidades)


def test_variavel_nova_reprova_o_mes():
    problemas = extracao.checar_mes(mes_com("12606", "11602", "99999"), METADADOS_MINIMOS, LOCALIDADES_MINIMAS)
    assert any("variáveis" in p for p in problemas)


def test_territorio_fora_das_localidades_reprova_o_mes():
    linhas = mes_com("12606", "11602", territorio="99")
    problemas = extracao.checar_mes(linhas, METADADOS_MINIMOS, LOCALIDADES_MINIMAS)
    assert any("territórios" in p for p in problemas)


def extrair(tmp_path, modo, controle_hash, conteudo=b"[]"):
    """Roda a extração de um mês com a fonte e o banco simulados."""
    cursor = CursorFalso()
    sessao = SessaoFalsa({"/values": conteudo})
    controle = {202501: {"data_fonte": D1, "hash": controle_hash, "carregado_em": D1, "completo": True}} if controle_hash else {}
    resumo = extracao.extrair_periodos(
        sessao, ConexaoFalsa(cursor), cursor, tmp_path, {202501: D2}, controle, [202501], modo, "exec",
    )
    return resumo, cursor


def test_auto_com_hash_igual_nao_grava_arquivo(tmp_path):
    resumo, cursor = extrair(tmp_path, "auto", HASH_A)
    assert resumo == {"gravados": 0, "sem_mudanca": 1, "meses_gravados": []}
    assert not list(tmp_path.rglob("dados.json.gz"))
    # A data da fonte é atualizada, para o mês não parecer novidade amanhã.
    assert "UPDATE controle.carga_periodo SET data_fonte" in cursor.sql_executado()


def test_auto_com_hash_diferente_grava_e_deixa_pendente(tmp_path):
    resumo, cursor = extrair(tmp_path, "auto", "outro-hash")
    assert resumo == {"gravados": 1, "sem_mudanca": 0, "meses_gravados": [202501]}
    assert len(list(tmp_path.rglob("dados.json.gz"))) == 1
    assert "carregado_em = NULL" in cursor.sql_executado()


def test_completa_regrava_sem_comparar(tmp_path):
    resumo, _ = extrair(tmp_path, "completa", HASH_A)
    assert resumo == {"gravados": 1, "sem_mudanca": 0, "meses_gravados": [202501]}


def test_log_identifica_os_meses_gravados(tmp_path, caplog):
    with caplog.at_level("INFO"):
        extrair(tmp_path, "completa", HASH_A)
    assert "202501" in caplog.text


def test_resposta_que_nao_e_json_e_estrutura_alterada(tmp_path):
    with pytest.raises(fonte.EstruturaAlterada):
        extrair(tmp_path, "auto", None, conteudo=b"<html>erro</html>")


def recurso_gravado(tmp_path, conteudo: bytes) -> Path:
    arquivo = tmp_path / "metadados.json.gz"
    arquivo.write_bytes(gzip.compress(conteudo))
    return arquivo


def test_recurso_com_hash_igual_nao_cria_pasta_nova(tmp_path):
    cursor = CursorFalso({"FROM controle.carga_recurso": [(HASH_A, "arquivo")]})
    extracao.gravar_recurso(cursor, tmp_path, "metadados", b"[]", "url", "exec")
    assert not list(tmp_path.rglob("dados.json.gz"))


def metadados_com(*variaveis, nome="x") -> bytes:
    return json.dumps({
        "variaveis": [{"id": v, "nome": nome} for v in variaveis],
        "classificacoes": [{"categorias": [{"id": 129320, "nome": nome}]}],
    }).encode()


def cursor_com_versao_anterior(tmp_path, conteudo: bytes) -> CursorFalso:
    anterior = recurso_gravado(tmp_path, conteudo)
    return CursorFalso({"SELECT hash_conteudo, arquivo": [("hash-anterior", str(anterior))]})


def test_variavel_nova_nos_metadados_interrompe_sem_gravar(tmp_path):
    cursor = cursor_com_versao_anterior(tmp_path, metadados_com(12606))
    with pytest.raises(fonte.EstruturaAlterada, match="99999"):
        extracao.gravar_recurso(cursor, tmp_path, "metadados", metadados_com(12606, 99999), "url", "exec")
    assert not list(tmp_path.rglob("dados.json.gz"))


def test_variavel_removida_nos_metadados_interrompe(tmp_path):
    cursor = cursor_com_versao_anterior(tmp_path, metadados_com(12606, 11602))
    with pytest.raises(fonte.EstruturaAlterada):
        extracao.gravar_recurso(cursor, tmp_path, "metadados", metadados_com(12606), "url", "exec")


def test_territorio_novo_nas_localidades_interrompe(tmp_path):
    anterior = json.dumps({"N3": [{"id": "23"}]}).encode()
    novo = json.dumps({"N3": [{"id": "23"}, {"id": "99"}]}).encode()
    cursor = cursor_com_versao_anterior(tmp_path, anterior)
    with pytest.raises(fonte.EstruturaAlterada, match="99"):
        extracao.gravar_recurso(cursor, tmp_path, "localidades", novo, "url", "exec")


def test_nome_alterado_sem_mudar_codigos_cria_nova_versao(tmp_path):
    cursor = cursor_com_versao_anterior(tmp_path, metadados_com(12606, nome="antigo"))
    extracao.gravar_recurso(cursor, tmp_path, "metadados", metadados_com(12606, nome="novo"), "url", "exec")
    assert len(list(tmp_path.rglob("dados.json.gz"))) == 1


def test_carga_completa_aceita_a_mudanca_de_estrutura(tmp_path):
    cursor = cursor_com_versao_anterior(tmp_path, metadados_com(12606))
    extracao.gravar_recurso(
        cursor, tmp_path, "metadados", metadados_com(12606, 99999), "url", "exec", aceitar_mudanca=True
    )
    assert len(list(tmp_path.rglob("dados.json.gz"))) == 1


def test_recurso_novo_cria_pasta_com_manifesto(tmp_path):
    cursor = CursorFalso()
    extracao.gravar_recurso(cursor, tmp_path, "metadados", b"[]", "url", "exec")
    manifesto = next(tmp_path.rglob("manifesto.json"))
    assert json.loads(manifesto.read_text(encoding="utf-8"))["url"] == "url"
    assert "INSERT INTO controle.carga_recurso" in cursor.sql_executado()


def test_ler_recurso_sem_registro_e_sem_dado_bruto():
    with pytest.raises(extracao.SemDadoBruto):
        extracao.ler_recurso(CursorFalso(), "metadados")


def test_ler_recurso_com_arquivo_apagado_e_sem_dado_bruto(tmp_path):
    cursor = CursorFalso({"FROM controle.carga_recurso": [(str(tmp_path / "nao-existe.gz"),)]})
    with pytest.raises(extracao.SemDadoBruto):
        extracao.ler_recurso(cursor, "metadados")


def cursor_para_validar(tmp_path, linhas: list[dict]) -> CursorFalso:
    arquivos = {}
    for recurso, conteudo in (("metadados", METADADOS_MINIMOS), ("localidades", LOCALIDADES_MINIMAS)):
        arquivo = tmp_path / f"{recurso}.json.gz"
        arquivo.write_bytes(gzip.compress(json.dumps(conteudo).encode()))
        arquivos[recurso] = str(arquivo)
    mes = tmp_path / "mes.json.gz"
    mes.write_bytes(gzip.compress(json.dumps(linhas).encode()))

    class Cursor(CursorFalso):
        def execute(self, sql, parametros=None):
            super().execute(sql, parametros)
            if "FROM controle.carga_recurso" in sql:
                self._ultimo = [(arquivos[parametros[0]],)]
            elif "FROM controle.carga_periodo" in sql:
                self._ultimo = [(202501, str(mes))]

    return Cursor()


def test_validar_brutos_nao_acessa_a_fonte(tmp_path, monkeypatch):
    # Antes, a validação baixava os metadados mesmo no modo reprocessar.
    monkeypatch.setattr(fonte, "criar_sessao", lambda: pytest.fail("acessou a fonte"))
    extracao.validar_brutos(cursor_para_validar(tmp_path, mes_com("12606", "11602")))


def test_validar_brutos_reprova_mudanca_de_estrutura(tmp_path):
    with pytest.raises(fonte.EstruturaAlterada, match="202501"):
        extracao.validar_brutos(cursor_para_validar(tmp_path, mes_com("12606")))


def test_reprocessar_mes_sem_registro_e_sem_dado_bruto(tmp_path):
    controle = {202501: {"data_fonte": D1, "hash": "h", "carregado_em": D1, "completo": True, "arquivo": str(tmp_path / "x.gz")}}
    with pytest.raises(extracao.SemDadoBruto):
        extracao.marcar_para_reprocessar(CursorFalso(), controle, 202502, 202502)


def test_reprocessar_com_arquivo_apagado_e_sem_dado_bruto(tmp_path):
    controle = {202501: {"data_fonte": D1, "hash": "h", "carregado_em": D1, "completo": True, "arquivo": str(tmp_path / "x.gz")}}
    with pytest.raises(extracao.SemDadoBruto):
        extracao.marcar_para_reprocessar(CursorFalso(), controle, None, None)


def test_reprocessar_sem_nenhuma_carga_e_sem_dado_bruto():
    with pytest.raises(extracao.SemDadoBruto):
        extracao.marcar_para_reprocessar(CursorFalso(), {}, None, None)
