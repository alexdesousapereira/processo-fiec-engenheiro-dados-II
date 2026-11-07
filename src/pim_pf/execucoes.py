"""Registro das execuções de ingestão em controle.execucao_ingestao.

O estado fica no banco para sobreviver a reinícios da API e para o próprio banco impedir,
pelo índice único parcial, duas execuções em aberto.
"""
import json
import logging
import uuid

import psycopg2

from pim_pf import banco

log = logging.getLogger(__name__)

COLUNAS = (
    "execucao_id, tabela, modo, inicio, fim, situacao, periodos_gravados, periodos_sem_mudanca, "
    "periodos_parciais, meses_gravados, meses_stage, linhas_stage, nulos_stage, causa_tipo, causa_mensagem, "
    "criada_em, iniciada_em, concluida_em"
)


class ExecucaoEmAndamento(Exception):
    """Já existe uma execução em aberto, que o pedido recusado pode acompanhar."""

    def __init__(self, execucao_id: str) -> None:
        super().__init__(f"Execução em andamento: {execucao_id}")
        self.execucao_id = execucao_id


def criar(tabela: str, modo: str, inicio: int | None, fim: int | None) -> str:
    execucao_id = str(uuid.uuid4())
    try:
        with banco.abrir() as conexao, conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO controle.execucao_ingestao (execucao_id, tabela, modo, inicio, fim) "
                "VALUES (%s, %s, %s, %s, %s)",
                (execucao_id, tabela, modo, inicio, fim),
            )
    except psycopg2.errors.UniqueViolation as erro:
        raise ExecucaoEmAndamento(_execucao_em_aberto()) from erro
    return execucao_id


def _execucao_em_aberto() -> str:
    with banco.abrir() as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "SELECT execucao_id FROM controle.execucao_ingestao WHERE situacao IN ('pendente', 'executando')"
        )
        registro = cursor.fetchone()
    return registro[0] if registro else "desconhecida"


def iniciar(execucao_id: str) -> None:
    with banco.abrir() as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "UPDATE controle.execucao_ingestao SET situacao = 'executando', iniciada_em = now() "
            "WHERE execucao_id = %s AND situacao = 'pendente'",
            (execucao_id,),
        )


def concluir(execucao_id: str, resumo: dict) -> None:
    with banco.abrir() as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "UPDATE controle.execucao_ingestao SET situacao = 'sucesso', concluida_em = now(), "
            "periodos_gravados = %s, periodos_sem_mudanca = %s, periodos_parciais = %s, "
            "meses_gravados = %s, meses_stage = %s, linhas_stage = %s, nulos_stage = %s "
            "WHERE execucao_id = %s AND situacao = 'executando'",
            (
                resumo["periodos_gravados"], resumo["periodos_sem_mudanca"], resumo["periodos_parciais"],
                resumo["meses_gravados"], resumo["meses_stage"],
                json.dumps(resumo["linhas_stage"]), json.dumps(resumo["nulos_stage"]), execucao_id,
            ),
        )


def falhar(execucao_id: str, tipo: str, mensagem: str) -> None:
    with banco.abrir() as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "UPDATE controle.execucao_ingestao SET situacao = 'falha', concluida_em = now(), "
            "causa_tipo = %s, causa_mensagem = %s "
            "WHERE execucao_id = %s",
            (tipo, mensagem, execucao_id),
        )


def consultar(execucao_id: str) -> dict | None:
    with banco.abrir() as conexao, conexao.cursor() as cursor:
        cursor.execute(f"SELECT {COLUNAS} FROM controle.execucao_ingestao WHERE execucao_id = %s", (execucao_id,))
        registro = cursor.fetchone()
    if registro is None:
        return None
    execucao = dict(zip(COLUNAS.split(", "), registro))
    tipo, mensagem = execucao.pop("causa_tipo"), execucao.pop("causa_mensagem")
    execucao["causa"] = {"tipo": tipo, "mensagem": mensagem} if tipo else None
    return execucao


def marcar_interrompidas() -> int:
    """Roda ao iniciar a API. O que estava em aberto morreu com o processo anterior."""
    with banco.abrir() as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "UPDATE controle.execucao_ingestao SET situacao = 'interrompida', concluida_em = now() "
            "WHERE situacao IN ('pendente', 'executando')"
        )
        quantidade = cursor.rowcount
    if quantidade:
        log.warning("Execuções interrompidas pelo reinício da API: %d", quantidade)
    return quantidade
