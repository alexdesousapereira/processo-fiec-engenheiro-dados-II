"""Cliente das APIs públicas do IBGE. Fatos medidos em docs/fonte-sidra-8888.md."""
from datetime import date, datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL_AGREGADOS = "https://servicodados.ibge.gov.br/api/v3/agregados/8888"
# /h/n retira a linha de cabeçalho. Um mês por requisição mantém o hash por mês.
URL_VALORES = "https://apisidra.ibge.gov.br/values/t/8888/n1/all/n2/all/n3/all/v/all/p/{periodo}/c544/all/f/a/h/n"
URL_METADADOS = f"{URL_AGREGADOS}/metadados"
URL_LOCALIDADES = f"{URL_AGREGADOS}/localidades/{{nivel}}"
NIVEIS_TERRITORIAIS = ("N1", "N2", "N3")
TEMPO_LIMITE = 120


class FonteIndisponivel(Exception):
    """A fonte falhou mesmo depois das novas tentativas."""


class EstruturaAlterada(Exception):
    """A resposta não tem o formato ou a quantidade de dados esperados."""


def criar_sessao() -> requests.Session:
    """Sessão que repete falhas temporárias da API. O requests já descompacta o gzip."""
    tentativas = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    sessao = requests.Session()
    sessao.mount("https://", HTTPAdapter(max_retries=tentativas))
    return sessao


def _baixar(sessao: requests.Session, url: str) -> requests.Response:
    try:
        resposta = sessao.get(url, timeout=TEMPO_LIMITE)
        resposta.raise_for_status()
    except requests.RequestException as erro:
        raise FonteIndisponivel(f"Falha ao acessar {url}: {type(erro).__name__}") from erro
    return resposta


def _ler_json(resposta: requests.Response, url: str) -> dict | list:
    try:
        return resposta.json()
    except ValueError as erro:
        raise EstruturaAlterada(f"Resposta de {url} não é JSON") from erro


def buscar_periodos(sessao: requests.Session) -> dict[int, date]:
    """Devolve cada período com a data de modificação informada pela fonte."""
    url = f"{URL_AGREGADOS}/periodos"
    itens = _ler_json(_baixar(sessao, url), url)
    try:
        return {int(item["id"]): datetime.strptime(item["modificacao"], "%d/%m/%Y").date() for item in itens}
    except (KeyError, TypeError, ValueError) as erro:
        raise EstruturaAlterada(f"Períodos em formato inesperado: {erro}") from erro


def _validar_metadados(metadados: dict) -> None:
    try:
        variaveis = metadados["variaveis"]
        categorias = metadados["classificacoes"][0]["categorias"]
        if not variaveis or not categorias:
            raise ValueError("lista vazia")
        for variavel in variaveis:
            variavel["id"], variavel["nome"], variavel["unidade"]
        for categoria in categorias:
            categoria["id"], categoria["nome"]
    except (KeyError, IndexError, TypeError, ValueError) as erro:
        raise EstruturaAlterada(f"Metadados em formato inesperado: {erro!r}") from erro


def buscar_metadados(sessao: requests.Session) -> bytes:
    """Devolve a resposta original, em bytes, depois de conferir a estrutura."""
    resposta = _baixar(sessao, URL_METADADOS)
    _validar_metadados(_ler_json(resposta, URL_METADADOS))
    return resposta.content


def buscar_localidades(sessao: requests.Session) -> bytes:
    """Junta os três níveis em um só JSON, mantendo os bytes de cada resposta da fonte."""
    partes = []
    for nivel in NIVEIS_TERRITORIAIS:
        url = URL_LOCALIDADES.format(nivel=nivel)
        resposta = _baixar(sessao, url)
        itens = _ler_json(resposta, url)
        if not isinstance(itens, list) or not itens:
            raise EstruturaAlterada(f"Nível {nivel} sem localidades")
        partes.append(f'"{nivel}":'.encode() + resposta.content)
    return b"{" + b",".join(partes) + b"}"


def url_valores(periodo: int) -> str:
    return URL_VALORES.format(periodo=periodo)


def buscar_valores(sessao: requests.Session, periodo: int) -> bytes:
    """Devolve a resposta original, em bytes, para ser guardada sem alteração."""
    return _baixar(sessao, url_valores(periodo)).content
