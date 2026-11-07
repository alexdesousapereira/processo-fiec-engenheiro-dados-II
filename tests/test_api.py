"""Testes da API com o banco e a extração simulados (contracts/api-ingestao.md)."""
from datetime import datetime, timezone

import psycopg2
import pytest
from fastapi.testclient import TestClient

from pim_pf import api, banco, carga, execucoes, extracao, fonte, tratamento

cliente = TestClient(api.app)
RESUMO = {
    "periodos_gravados": 1,
    "periodos_sem_mudanca": 2,
    "periodos_parciais": [202609],
    "meses_gravados": [202608],
    "meses_stage": [202608],
    "linhas_stage": {"producao_fisica": 3078},
    "nulos_stage": {"producao_fisica": 10},
}


class RegistroFalso:
    """Guarda as execuções em memória, no lugar de controle.execucao_ingestao."""

    def __init__(self):
        self.linhas: dict[str, dict] = {}
        self.em_aberto: str | None = None

    def criar(self, tabela, modo, inicio, fim):
        if self.em_aberto:
            raise execucoes.ExecucaoEmAndamento(self.em_aberto)
        execucao_id = f"exec-{len(self.linhas) + 1}"
        self.linhas[execucao_id] = {
            "execucao_id": execucao_id, "tabela": tabela, "modo": modo, "inicio": inicio, "fim": fim,
            "situacao": "pendente", "periodos_gravados": 0, "periodos_sem_mudanca": 0, "periodos_parciais": [],
            "meses_gravados": [], "meses_stage": [], "linhas_stage": {}, "nulos_stage": {}, "causa": None,
            "criada_em": datetime(2026, 11, 7, tzinfo=timezone.utc), "iniciada_em": None, "concluida_em": None,
        }
        return execucao_id

    def iniciar(self, execucao_id):
        self.linhas[execucao_id]["situacao"] = "executando"

    def concluir(self, execucao_id, resumo):
        self.linhas[execucao_id].update(resumo, situacao="sucesso")

    def falhar(self, execucao_id, tipo, mensagem):
        self.linhas[execucao_id].update(situacao="falha", causa={"tipo": tipo, "mensagem": mensagem})

    def consultar(self, execucao_id):
        return self.linhas.get(execucao_id)

    def marcar_interrompidas(self):
        self.em_aberto = None
        return 1


@pytest.fixture
def registro(monkeypatch):
    falso = RegistroFalso()
    for nome in ("criar", "iniciar", "concluir", "falhar", "consultar", "marcar_interrompidas"):
        monkeypatch.setattr(execucoes, nome, getattr(falso, nome))
    monkeypatch.setattr(api, "_em_execucao", set())
    return falso


@pytest.fixture
def extracao_ok(monkeypatch, registro):
    chamadas = []

    def executar(tabela, modo, inicio, fim, execucao_id):
        chamadas.append((tabela, modo, inicio, fim, execucao_id))
        return RESUMO

    monkeypatch.setattr(carga, "executar_extracao", executar)
    return chamadas


def test_health_com_banco_no_ar(banco_falso, cursor_falso):
    banco_falso(cursor_falso)
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_health_sem_banco(monkeypatch):
    def recusar():
        raise psycopg2.OperationalError("senha ou host em detalhe")

    monkeypatch.setattr(banco, "conectar", recusar)
    resposta = cliente.get("/health")
    assert resposta.status_code == 503
    assert resposta.json() == {"status": "indisponivel"}


@pytest.mark.parametrize(
    "rota, tabela",
    [
        ("variaveis", "variaveis"), ("categoria", "categoria"), ("territorio", "territorio"),
        ("producao-fisica", "producao_fisica"),
    ],
)
def test_cada_endpoint_aciona_a_sua_tabela(extracao_ok, rota, tabela):
    resposta = cliente.post(f"/extracoes/{rota}", json={})
    assert resposta.status_code == 202
    corpo = resposta.json()
    assert corpo["situacao"] == "pendente"
    assert corpo["status_url"] == f"/execucoes/{corpo['execucao_id']}"
    assert extracao_ok == [(tabela, "auto", None, None, corpo["execucao_id"])]


def test_pedido_sem_corpo_usa_o_padrao(extracao_ok):
    assert cliente.post("/extracoes/producao-fisica").status_code == 202


def test_tabela_desconhecida_e_recusada(extracao_ok):
    assert cliente.post("/extracoes/outra", json={}).status_code == 422
    assert extracao_ok == []


def test_intervalo_chega_como_periodo(extracao_ok):
    cliente.post("/extracoes/producao-fisica", json={"inicio": "2025-01", "fim": "2025-03"})
    assert extracao_ok[0][2:4] == (202501, 202503)


@pytest.mark.parametrize(
    "corpo",
    [
        {"inicio": "2025-13", "fim": "2025-13"},
        {"inicio": "202501", "fim": "202503"},
        {"inicio": "2025-03", "fim": "2025-01"},
        {"inicio": "2025-01"},
        {"fim": "2025-01"},
        {"inicio": "2023-01", "fim": "2025-01"},
        {"modo": "completa", "inicio": "2025-01", "fim": "2025-02"},
        {"modo": "outro"},
        {"campo_extra": 1},
    ],
)
def test_pedido_invalido_nao_executa_nada(extracao_ok, corpo):
    assert cliente.post("/extracoes/producao-fisica", json=corpo).status_code == 422
    assert extracao_ok == []


def test_intervalo_de_exatos_24_meses_e_aceito(extracao_ok):
    resposta = cliente.post("/extracoes/producao-fisica", json={"inicio": "2023-01", "fim": "2024-12"})
    assert resposta.status_code == 202


@pytest.mark.parametrize(
    "corpo",
    [{"inicio": "2025-01", "fim": "2025-01"}, {"modo": "completa"}],
)
def test_dimensao_nao_aceita_periodo_nem_carga_completa(extracao_ok, corpo):
    assert cliente.post("/extracoes/variaveis", json=corpo).status_code == 422


def test_dimensao_aceita_reprocessar(extracao_ok):
    assert cliente.post("/extracoes/territorio", json={"modo": "reprocessar"}).status_code == 202


def test_execucao_em_aberto_recusa_o_pedido_e_informa_qual_e(registro, extracao_ok):
    registro.em_aberto = "exec-em-andamento"
    api._em_execucao.add("exec-em-andamento")
    resposta = cliente.post("/extracoes/variaveis", json={})
    assert resposta.status_code == 409
    assert resposta.json() == {"detail": "Já há uma execução em aberto.", "execucao_id": "exec-em-andamento"}
    assert extracao_ok == []


def test_execucao_aberta_que_este_processo_nao_roda_e_liberada(registro, extracao_ok):
    # O banco caiu ao registrar o fim de uma execução: sem isso, a API recusaria tudo até reiniciar.
    registro.em_aberto = "exec-perdida"
    resposta = cliente.post("/extracoes/variaveis", json={})
    assert resposta.status_code == 202
    assert len(extracao_ok) == 1


def test_falha_ao_iniciar_vira_falha_registrada(monkeypatch, registro, extracao_ok):
    def recusar(_):
        raise psycopg2.OperationalError("banco fora")

    monkeypatch.setattr(execucoes, "iniciar", recusar)
    criada = cliente.post("/extracoes/variaveis", json={}).json()
    assert registro.linhas[criada["execucao_id"]]["situacao"] == "falha"
    assert extracao_ok == []
    assert api._em_execucao == set()


def test_falha_ao_registrar_o_fim_nao_derruba_o_processo(monkeypatch, registro, extracao_ok):
    def recusar(*_):
        raise psycopg2.OperationalError("banco fora")

    monkeypatch.setattr(execucoes, "concluir", recusar)
    monkeypatch.setattr(execucoes, "falhar", recusar)
    assert cliente.post("/extracoes/variaveis", json={}).status_code == 202
    assert api._em_execucao == set()


def test_documentacao_declara_os_modelos_de_saude_e_de_conflito():
    caminhos = cliente.get("/openapi.json").json()["paths"]
    saude = caminhos["/health"]["get"]["responses"]
    assert "$ref" in saude["200"]["content"]["application/json"]["schema"]
    conflito = caminhos["/extracoes/producao-fisica"]["post"]["responses"]["409"]
    assert "$ref" in conflito["content"]["application/json"]["schema"]


def test_status_mostra_o_resultado(extracao_ok):
    criada = cliente.post("/extracoes/producao-fisica", json={}).json()
    status = cliente.get(criada["status_url"]).json()
    assert status["situacao"] == "sucesso"
    assert status["periodos_gravados"] == 1
    assert status["periodos_parciais"] == [202609]
    assert status["meses_gravados"] == [202608]
    assert status["meses_stage"] == [202608]
    assert status["linhas_stage"] == {"producao_fisica": 3078}
    assert status["causa"] is None


def test_execucao_inexistente_devolve_404(registro):
    assert cliente.get("/execucoes/nao-existe").status_code == 404


@pytest.mark.parametrize(
    "erro, tipo",
    [
        (fonte.FonteIndisponivel("fora do ar"), "fonte_indisponivel"),
        (fonte.EstruturaAlterada("mudou"), "estrutura_alterada"),
        (tratamento.DadosInvalidos("símbolo"), "dados_invalidos"),
        (extracao.PeriodosIndisponiveis("202707"), "periodos_indisponiveis"),
        (extracao.SemDadoBruto("sem arquivo"), "sem_dado_bruto"),
    ],
)
def test_cada_erro_vira_a_causa_certa(monkeypatch, registro, erro, tipo):
    def falhar(*_):
        raise erro

    monkeypatch.setattr(carga, "executar_extracao", falhar)
    criada = cliente.post("/extracoes/producao-fisica", json={}).json()
    status = cliente.get(criada["status_url"]).json()
    assert status["situacao"] == "falha"
    assert status["causa"] == {"tipo": tipo, "mensagem": str(erro)}


def test_erro_inesperado_nao_expoe_detalhes(monkeypatch, registro):
    def falhar(*_):
        raise RuntimeError("senha=segredo em /caminho/interno")

    monkeypatch.setattr(carga, "executar_extracao", falhar)
    criada = cliente.post("/extracoes/producao-fisica", json={}).json()
    causa = cliente.get(criada["status_url"]).json()["causa"]
    assert causa["tipo"] == "erro_interno"
    assert "segredo" not in causa["mensagem"]


def test_novidades(monkeypatch):
    resultado = {"ha_novidade": True, "meses_alterados": [202609], "meses_pendentes": []}
    monkeypatch.setattr(extracao, "verificar_novidades", lambda: resultado)
    resposta = cliente.get("/fonte/novidades")
    assert resposta.status_code == 200
    assert resposta.json() == resultado


def test_novidades_com_a_fonte_fora_devolve_503(monkeypatch):
    def falhar():
        raise fonte.FonteIndisponivel("https://interno")

    monkeypatch.setattr(extracao, "verificar_novidades", falhar)
    resposta = cliente.get("/fonte/novidades")
    assert resposta.status_code == 503
    assert "interno" not in resposta.text


def test_inicio_da_api_marca_execucoes_abertas_como_interrompidas(monkeypatch):
    chamadas = []
    monkeypatch.setattr(execucoes, "marcar_interrompidas", lambda: chamadas.append(1) or 0)
    with TestClient(api.app):
        pass
    assert chamadas == [1]
