import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
import requests
from conftest import RespostaFalsa

from pim_pf import cliente_api

URL = "http://ingestao:8000"


@pytest.fixture
def api(monkeypatch):
    """Simula a API e guarda as chamadas feitas pela DAG."""
    monkeypatch.setenv("PIM_API_URL", URL)
    estado = {"resposta": RespostaFalsa({}), "chamadas": []}

    class Sessao:
        def _chamar(self, metodo, url, timeout, json=None):
            estado["chamadas"].append({"metodo": metodo, "url": url, "timeout": timeout, "json": json})
            return estado["resposta"]

        def get(self, url, timeout=None):
            return self._chamar("get", url, timeout)

        def post(self, url, json=None, timeout=None):
            return self._chamar("post", url, timeout, json)

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    monkeypatch.setattr(cliente_api, "criar_sessao", Sessao)
    return estado


def test_solicitar_devolve_o_identificador(api):
    api["resposta"] = RespostaFalsa({"execucao_id": "exec-1"}, status=202)
    assert cliente_api.solicitar("auto", "", "") == "exec-1"
    assert api["chamadas"][0]["url"] == f"{URL}/extracoes/producao-fisica"
    assert api["chamadas"][0]["json"] == {"modo": "auto"}


def test_solicitar_repassa_o_intervalo(api):
    api["resposta"] = RespostaFalsa({"execucao_id": "exec-1"}, status=202)
    cliente_api.solicitar("reprocessar", "2025-01", "2025-02")
    assert api["chamadas"][0]["json"] == {"modo": "reprocessar", "inicio": "2025-01", "fim": "2025-02"}


def test_nova_tentativa_adota_a_execucao_que_ja_esta_rodando(api):
    # Sem isso, repetir a tarefa falharia só porque o primeiro pedido foi aceito.
    api["resposta"] = RespostaFalsa({"detail": "...", "execucao_id": "exec-aberta"}, status=409)
    assert cliente_api.solicitar("auto", "", "") == "exec-aberta"


def test_pedido_invalido_falha_a_tarefa(api):
    api["resposta"] = RespostaFalsa({"detail": "..."}, status=422)
    with pytest.raises(requests.HTTPError):
        cliente_api.solicitar("auto", "2025-03", "2025-01")


@pytest.mark.parametrize("situacao", ["pendente", "executando"])
def test_execucao_em_aberto_ainda_nao_concluiu(api, situacao):
    api["resposta"] = RespostaFalsa({"situacao": situacao})
    assert cliente_api.execucao_concluida("exec-1") is False
    assert api["chamadas"][0]["url"] == f"{URL}/execucoes/exec-1"


def test_execucao_com_sucesso_concluiu(api):
    api["resposta"] = RespostaFalsa({"situacao": "sucesso"})
    assert cliente_api.execucao_concluida("exec-1") is True


def test_execucao_com_falha_interrompe_a_dag_com_a_causa(api):
    api["resposta"] = RespostaFalsa({"situacao": "falha", "causa": {"tipo": "dados_invalidos", "mensagem": "símbolo"}})
    with pytest.raises(cliente_api.ExecucaoFalhou, match="dados_invalidos"):
        cliente_api.execucao_concluida("exec-1")


def test_execucao_interrompida_interrompe_a_dag(api):
    api["resposta"] = RespostaFalsa({"situacao": "interrompida", "causa": None})
    with pytest.raises(cliente_api.ExecucaoFalhou, match="interrompida"):
        cliente_api.execucao_concluida("exec-1")


@pytest.mark.parametrize("valor", [True, False])
def test_ha_novidade_le_a_api(api, valor):
    api["resposta"] = RespostaFalsa({"ha_novidade": valor})
    assert cliente_api.ha_novidade() is valor
    assert api["chamadas"][0]["url"] == f"{URL}/fonte/novidades"


def test_toda_chamada_tem_tempo_limite(api):
    api["resposta"] = RespostaFalsa({"ha_novidade": False, "situacao": "sucesso", "execucao_id": "e"})
    cliente_api.ha_novidade()
    cliente_api.solicitar("auto", "", "")
    cliente_api.execucao_concluida("e")
    assert all(c["timeout"] == cliente_api.TEMPO_LIMITE for c in api["chamadas"])


@pytest.fixture
def servidor(monkeypatch):
    """Servidor HTTP real, porque quem repete as chamadas é o adaptador da sessão."""
    estado = {"respostas": [], "pedidos": 0}

    class Tratador(BaseHTTPRequestHandler):
        def _responder(self):
            estado["pedidos"] += 1
            status, corpo = estado["respostas"].pop(0)
            dados = json.dumps(corpo).encode()
            self.send_response(status)
            self.send_header("Content-Length", str(len(dados)))
            self.end_headers()
            self.wfile.write(dados)

        do_GET = do_POST = _responder

        def log_message(self, *_):
            pass

    http = HTTPServer(("127.0.0.1", 0), Tratador)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    monkeypatch.setenv("PIM_API_URL", f"http://127.0.0.1:{http.server_port}")
    yield estado
    http.shutdown()
    http.server_close()


def test_falha_passageira_nao_derruba_o_sensor(servidor):
    # O sensor não tem novas tentativas: quem absorve a falha de rede é a sessão.
    servidor["respostas"] = [(503, {}), (200, {"situacao": "sucesso"})]
    assert cliente_api.execucao_concluida("exec-1") is True
    assert servidor["pedidos"] == 2


def test_pedido_de_extracao_nao_e_repetido_pela_sessao(servidor):
    # Repetir um POST que pode ter sido aceito criaria dúvida sobre qual execução acompanhar.
    servidor["respostas"] = [(503, {})]
    with pytest.raises(requests.HTTPError):
        cliente_api.solicitar("auto", "", "")
    assert servidor["pedidos"] == 1
