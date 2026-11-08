"""Valida o JSON do PBIP contra os esquemas oficiais da Microsoft e confere os arquivos TMDL.

Uso, a partir da raiz do repositório (baixa os esquemas da internet):
    docker run --rm -v "$(pwd):/repo" -w /repo python:3.12.13-slim-bookworm sh -c \
      "pip install -q jsonschema==4.26.0 referencing==0.37.0 requests==2.34.2 && python powerbi/ferramentas/validar_pbip.py"

Só valida a estrutura: DAX, TMDL e o visual final só são confirmados no Power BI Desktop.
"""
import json
import logging
import re
import sys
from pathlib import Path

import requests
from jsonschema import Draft7Validator, validators
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

log = logging.getLogger("validar_pbip")
POWERBI = Path(__file__).resolve().parents[1]
EXTENSOES = ("*.json", "*.pbir", "*.pbip", "*.pbism")
_esquemas: dict[str, Resource] = {}


def baixar(uri: str) -> Resource:
    if uri not in _esquemas:
        resposta = requests.get(uri, timeout=60)
        resposta.raise_for_status()
        _esquemas[uri] = Resource.from_contents(resposta.json(), default_specification=DRAFT7)
    return _esquemas[uri]


_alternativos: dict[str, str] = {}


def esquema_publicado(uri: str) -> tuple[Resource, str]:
    """O Desktop grava versões que a Microsoft às vezes ainda não publicou (ex.: visualContainer 2.14.0).

    Nesse caso, usa a versão publicada mais próxima, descendo o número intermediário, e avisa uma vez.
    Devolve o esquema e o endereço efetivamente usado.
    """
    if uri in _alternativos:
        return baixar(_alternativos[uri]), _alternativos[uri]
    match = re.search(r"/(\d+)\.(\d+)\.(\d+)/schema\.json$", uri)
    try:
        return baixar(uri), uri
    except requests.HTTPError:
        if not match:
            raise
    maior, menor = int(match.group(1)), int(match.group(2))
    for candidato in range(menor - 1, -1, -1):
        alternativo = uri[: match.start()] + f"/{maior}.{candidato}.0/schema.json"
        try:
            recurso = baixar(alternativo)
        except requests.HTTPError:
            continue
        log.warning("Esquema %s não publicado; validando com %s", uri.split("definition/")[-1], alternativo.split("definition/")[-1])
        _alternativos[uri] = alternativo
        return recurso, alternativo
    raise LookupError(f"Nenhum esquema publicado para {uri}")


def arquivos() -> list[Path]:
    encontrados = [a for ext in EXTENSOES for a in POWERBI.rglob(ext)]
    return sorted(a for a in encontrados if "ferramentas" not in a.parts)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    falhas = total = 0
    for arquivo in arquivos():
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
        uri = dados.get("$schema")
        if not uri:
            continue  # tema e tema-base não declaram esquema
        total += 1
        recurso, usado = esquema_publicado(uri)
        esquema = recurso.contents
        dados["$schema"] = usado  # o esquema alternativo exige o próprio endereço nesse campo
        classe = validators.validator_for(esquema, default=Draft7Validator)
        erros = list(classe(esquema, registry=Registry(retrieve=baixar)).iter_errors(dados))
        for erro in erros[:6]:
            caminho = "/".join(str(p) for p in erro.absolute_path)
            log.error("%s %s: %s", arquivo.relative_to(POWERBI), caminho, erro.message[:170])
        falhas += bool(erros)

    tmdl = sorted(POWERBI.rglob("*.tmdl"))
    for arquivo in tmdl:
        texto = arquivo.read_text(encoding="utf-8")
        if "\r" in texto or texto.startswith("﻿"):
            log.error("%s: TMDL com CRLF ou BOM", arquivo.relative_to(POWERBI))
            falhas += 1
    log.info("JSON validados: %d, com erro: %d; TMDL conferidos: %d", total, falhas, len(tmdl))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
