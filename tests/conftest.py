"""Dublês compartilhados. Nenhum teste acessa a API real do IBGE."""
import json
from contextlib import contextmanager

import pytest

METADADOS = {
    "variaveis": [
        {"id": 12606, "nome": "PIMPF - Número-índice (2022=100)", "unidade": "Número-índice"},
        {"id": 11602, "nome": "PIMPF - Variação M/M-12", "unidade": "%"},
    ],
    "classificacoes": [
        {
            "id": 544,
            "categorias": [
                {"id": 129316, "nome": "3 Indústrias de transformação"},
                {"id": 129320, "nome": "3.13 Fabricação de produtos têxteis"},
                {"id": 56689, "nome": "3.20 Fabricação de produtos químicos"},
            ],
        }
    ],
}

LOCALIDADES = {
    "N1": [{"id": "1", "nome": "Brasil", "nivel": {"id": "N1"}}],
    "N2": [{"id": "2", "nome": "Nordeste", "nivel": {"id": "N2"}}],
    "N3": [{"id": "23", "nome": "Ceará", "nivel": {"id": "N3"}}],
}


def linha_valor(valor="145.03000", uf="23", variavel="12606", categoria="129320", periodo="202501", nivel="3"):
    """Uma linha como a API de valores devolve."""
    return {
        "NC": nivel, "NN": "Unidade da Federação", "MC": "30", "MN": "Número-índice", "V": valor,
        "D1C": uf, "D1N": "Ceará", "D2C": variavel, "D2N": "PIMPF - Número-índice (2022=100)",
        "D3C": periodo, "D3N": "janeiro 2025", "D4C": categoria, "D4N": "3.13 Fabricação de produtos têxteis",
    }


class CursorFalso:
    """Cursor que responde por trecho de SQL e guarda o que foi executado e copiado."""

    def __init__(self, respostas: dict[str, list] | None = None):
        self.respostas = respostas or {}
        self.comandos: list[tuple[str, object]] = []
        self.copias: dict[str, str] = {}
        self._ultimo: list = []
        self.rowcount = 0

    def execute(self, sql, parametros=None):
        self.comandos.append((sql, parametros))
        self._ultimo = next((r for trecho, r in self.respostas.items() if trecho in sql), [])
        self.rowcount = len(self._ultimo)

    def fetchall(self):
        return self._ultimo

    def fetchone(self):
        return self._ultimo[0] if self._ultimo else None

    def copy_expert(self, sql, buffer):
        self.copias[sql.split()[1]] = buffer.read()

    def sql_executado(self) -> str:
        return "\n".join(sql for sql, _ in self.comandos)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class ConexaoFalsa:
    def __init__(self, cursor: CursorFalso):
        self._cursor = cursor
        self.commits = 0

    def cursor(self):
        return self._cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        pass


@pytest.fixture
def cursor_falso():
    return CursorFalso()


@pytest.fixture
def banco_falso(monkeypatch):
    """Troca `banco.abrir` por uma conexão falsa e devolve a função que define o cursor usado."""
    from pim_pf import banco

    def instalar(cursor: CursorFalso) -> CursorFalso:
        @contextmanager
        def abrir():
            yield ConexaoFalsa(cursor)

        monkeypatch.setattr(banco, "abrir", abrir)
        return cursor

    return instalar


class SessaoFalsa:
    """Fonte falsa: registra as URLs pedidas e pode falhar."""

    def __init__(self, respostas: dict[str, object] | None = None, erro: Exception | None = None):
        self.respostas = respostas or {}
        self.erro = erro
        self.chamadas: list[tuple[str, object]] = []

    def get(self, url, timeout=None):
        self.chamadas.append((url, timeout))
        if self.erro:
            raise self.erro
        corpo = next((c for trecho, c in self.respostas.items() if trecho in url), [])
        return RespostaFalsa(corpo)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class RespostaFalsa:
    def __init__(self, corpo, status: int = 200):
        self.corpo = corpo
        self.status_code = status
        self.verificada = False

    @property
    def content(self) -> bytes:
        return self.corpo if isinstance(self.corpo, bytes) else json.dumps(self.corpo).encode()

    def json(self):
        return json.loads(self.content)

    def raise_for_status(self):
        self.verificada = True
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"HTTP {self.status_code}")
