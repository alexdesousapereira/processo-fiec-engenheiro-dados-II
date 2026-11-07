"""Conexão com o banco do pipeline. As credenciais vêm do ambiente (.env)."""
import os
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import connection


def conectar() -> connection:
    return psycopg2.connect(
        host=os.environ["PIM_DB_HOST"],
        port=os.environ["PIM_DB_PORTA"],
        dbname=os.environ["PIM_DB_NOME"],
        user=os.environ["PIM_DB_USUARIO"],
        password=os.environ["PIM_DB_SENHA"],
    )


@contextmanager
def abrir() -> Iterator[connection]:
    """Confirma a transação ao sair, desfaz em caso de erro e sempre fecha a conexão.

    O `with` do psycopg2 cuida só da transação. Sem fechar, um serviço que fica no ar,
    como a API, acumularia conexões abertas.
    """
    conexao = conectar()
    try:
        with conexao:
            yield conexao
    finally:
        conexao.close()
