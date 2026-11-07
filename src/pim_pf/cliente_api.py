"""Chamadas da DAG à API de ingestão. Só usa requests, para rodar na imagem do Airflow."""
import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Conexão e leitura. A leitura é longa porque /fonte/novidades consulta o IBGE com novas tentativas.
TEMPO_LIMITE = (10, 300)
ROTA_EXTRACAO = "/extracoes/producao-fisica"


class ExecucaoFalhou(Exception):
    """A extração terminou sem sucesso: não adianta seguir para o warehouse."""


def criar_sessao() -> requests.Session:
    """Repete só consultas. Um POST que falhou no meio pode ter sido aceito pela API."""
    tentativas = Retry(total=3, backoff_factor=2, status_forcelist=[502, 503, 504], allowed_methods=["GET"])
    sessao = requests.Session()
    sessao.mount("http://", HTTPAdapter(max_retries=tentativas))
    return sessao


def _url(rota: str) -> str:
    return f"{os.environ['PIM_API_URL']}{rota}"


def ha_novidade() -> bool:
    with criar_sessao() as sessao:
        resposta = sessao.get(_url("/fonte/novidades"), timeout=TEMPO_LIMITE)
    resposta.raise_for_status()
    return resposta.json()["ha_novidade"]


def solicitar(modo: str, inicio: str, fim: str) -> str:
    """Pede a extração e devolve o identificador da execução.

    A produção física carrega também as três dimensões. Se o pedido receber 409, a tarefa adota
    a execução em aberto: numa nova tentativa, ela pode ser justamente a do primeiro pedido.
    """
    corpo = {"modo": modo}
    if inicio:
        corpo["inicio"] = inicio
    if fim:
        corpo["fim"] = fim
    with criar_sessao() as sessao:
        resposta = sessao.post(_url(ROTA_EXTRACAO), json=corpo, timeout=TEMPO_LIMITE)
    if resposta.status_code == 409:
        return resposta.json()["execucao_id"]
    resposta.raise_for_status()
    return resposta.json()["execucao_id"]


def execucao_concluida(execucao_id: str) -> bool:
    """Usada pelo sensor: False mantém a espera, True libera, e uma falha encerra a DAG."""
    with criar_sessao() as sessao:
        resposta = sessao.get(_url(f"/execucoes/{execucao_id}"), timeout=TEMPO_LIMITE)
    resposta.raise_for_status()
    execucao = resposta.json()
    if execucao["situacao"] in ("falha", "interrompida"):
        causa = execucao.get("causa") or {}
        raise ExecucaoFalhou(
            f"Execução {execucao_id} {execucao['situacao']}: {causa.get('tipo')} {causa.get('mensagem')}"
        )
    return execucao["situacao"] == "sucesso"
