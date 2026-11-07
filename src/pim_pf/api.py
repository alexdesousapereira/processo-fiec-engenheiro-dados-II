"""API de ingestão: único ponto de entrada da extração (contracts/api-ingestao.md).

As rotas só validam e delegam. A regra de negócio fica em carga.py e extracao.py.
"""
import logging
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Literal

import psycopg2
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from pim_pf import banco, carga, execucoes, extracao, fonte, tratamento

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)

Mes = Annotated[str, StringConstraints(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]
TabelaDimensao = Literal["variaveis", "categoria", "territorio"]

# Erros esperados. A mensagem deles descreve o dado, não o ambiente, e pode ir para o status.
CAUSAS = (
    (fonte.FonteIndisponivel, "fonte_indisponivel"),
    (fonte.EstruturaAlterada, "estrutura_alterada"),
    (tratamento.DadosInvalidos, "dados_invalidos"),
    (extracao.PeriodosIndisponiveis, "periodos_indisponiveis"),
    (extracao.SemDadoBruto, "sem_dado_bruto"),
)


class PedidoProducao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    modo: Literal["auto", "completa", "reprocessar"] = "auto"
    inicio: Mes | None = None
    fim: Mes | None = None

    @model_validator(mode="after")
    def validar_periodo(self) -> "PedidoProducao":
        if (self.inicio is None) != (self.fim is None):
            raise ValueError("Informe inicio e fim juntos")
        if self.inicio is not None:
            if self.modo == "completa":
                raise ValueError("O modo completa não aceita intervalo")
            extracao.validar_intervalo(
                extracao.texto_para_periodo(self.inicio), extracao.texto_para_periodo(self.fim)
            )
        return self


class PedidoDimensao(BaseModel):
    """Uma dimensão não tem meses: ela vem inteira dos metadados da fonte."""

    model_config = ConfigDict(extra="forbid")

    modo: Literal["auto", "reprocessar"] = "auto"


class PedidoAceito(BaseModel):
    execucao_id: str
    situacao: str
    status_url: str


class Causa(BaseModel):
    tipo: str
    mensagem: str


class Execucao(BaseModel):
    execucao_id: str
    tabela: str
    modo: str
    inicio: int | None
    fim: int | None
    situacao: str
    periodos_gravados: int
    periodos_sem_mudanca: int
    periodos_parciais: list[int]
    meses_gravados: list[int]
    meses_stage: list[int]
    linhas_stage: dict[str, int]
    nulos_stage: dict[str, int]
    causa: Causa | None
    criada_em: datetime
    iniciada_em: datetime | None
    concluida_em: datetime | None


class Novidades(BaseModel):
    ha_novidade: bool
    meses_alterados: list[int]
    meses_pendentes: list[int]


class ExecucaoEmAberto(BaseModel):
    detail: str
    execucao_id: str


class Saude(BaseModel):
    status: Literal["ok", "indisponivel"]


# O que este processo está executando. Como há um só worker, uma execução aberta no banco
# que não esteja aqui ficou para trás, por exemplo se o banco caiu ao registrar o fim dela.
_em_execucao: set[str] = set()
_trava = threading.Lock()


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI) -> AsyncIterator[None]:
    execucoes.marcar_interrompidas()
    yield


app = FastAPI(
    title="Ingestão PIM-PF",
    description="Aciona e acompanha a extração da tabela 8888 do IBGE.",
    lifespan=ciclo_de_vida,
)


def _registrar_falha(execucao_id: str, erro: Exception) -> None:
    tipo = next((nome for classe, nome in CAUSAS if isinstance(erro, classe)), None)
    if tipo:
        log.warning("Execução %s falhou (%s): %s", execucao_id, tipo, erro)
        mensagem = str(erro)
    else:
        # O detalhe de um erro inesperado pode expor o ambiente, então fica só no log.
        log.error("Erro inesperado na execução %s", execucao_id, exc_info=erro)
        tipo, mensagem = "erro_interno", "Erro inesperado. Consulte o log da API."
    try:
        execucoes.falhar(execucao_id, tipo, mensagem)
    except psycopg2.Error:
        # O próximo pedido libera esta execução, ao ver que ela não está em _em_execucao.
        log.exception("Não foi possível registrar a falha da execução %s", execucao_id)


def _executar(execucao_id: str, tabela: str, modo: str, inicio: int | None, fim: int | None) -> None:
    """Roda em segundo plano, depois de a resposta 202 já ter sido enviada."""
    try:
        execucoes.iniciar(execucao_id)
        execucoes.concluir(execucao_id, carga.executar_extracao(tabela, modo, inicio, fim, execucao_id))
    except Exception as erro:
        _registrar_falha(execucao_id, erro)
    finally:
        _em_execucao.discard(execucao_id)


def _criar_execucao(tabela: str, modo: str, inicio: int | None, fim: int | None) -> str:
    """A trava mantém o registro no banco e _em_execucao coerentes entre pedidos simultâneos."""
    with _trava:
        try:
            execucao_id = execucoes.criar(tabela, modo, inicio, fim)
        except execucoes.ExecucaoEmAndamento as erro:
            if erro.execucao_id in _em_execucao:
                raise
            log.warning("Liberando a execução %s, que este processo não está rodando", erro.execucao_id)
            execucoes.marcar_interrompidas()
            execucao_id = execucoes.criar(tabela, modo, inicio, fim)
        _em_execucao.add(execucao_id)
    return execucao_id


def _aceitar(
    tarefas: BackgroundTasks, tabela: str, modo: str, inicio: int | None, fim: int | None
) -> PedidoAceito | JSONResponse:
    try:
        execucao_id = _criar_execucao(tabela, modo, inicio, fim)
    except execucoes.ExecucaoEmAndamento as erro:
        conflito = ExecucaoEmAberto(detail="Já há uma execução em aberto.", execucao_id=erro.execucao_id)
        return JSONResponse(conflito.model_dump(), status_code=409)
    tarefas.add_task(_executar, execucao_id, tabela, modo, inicio, fim)
    return PedidoAceito(execucao_id=execucao_id, situacao="pendente", status_url=f"/execucoes/{execucao_id}")


@app.post(
    "/extracoes/producao-fisica", status_code=202, response_model=PedidoAceito,
    responses={409: {"model": ExecucaoEmAberto}},
)
def extrair_producao(tarefas: BackgroundTasks, pedido: PedidoProducao | None = None) -> PedidoAceito | JSONResponse:
    """Extrai os valores e carrega a produção física e as três dimensões na Stage."""
    pedido = pedido or PedidoProducao()
    inicio = extracao.texto_para_periodo(pedido.inicio) if pedido.inicio else None
    fim = extracao.texto_para_periodo(pedido.fim) if pedido.fim else None
    return _aceitar(tarefas, extracao.PRODUCAO, pedido.modo, inicio, fim)


@app.post(
    "/extracoes/{tabela}", status_code=202, response_model=PedidoAceito,
    responses={409: {"model": ExecucaoEmAberto}},
)
def extrair_dimensao(
    tabela: TabelaDimensao, tarefas: BackgroundTasks, pedido: PedidoDimensao | None = None
) -> PedidoAceito | JSONResponse:
    """Extrai só a dimensão pedida, sem baixar valores."""
    return _aceitar(tarefas, tabela, (pedido or PedidoDimensao()).modo, None, None)


@app.get("/execucoes/{execucao_id}", response_model=Execucao)
def consultar_execucao(execucao_id: str) -> dict:
    execucao = execucoes.consultar(execucao_id)
    if execucao is None:
        raise HTTPException(status_code=404, detail="Execução não encontrada.")
    return execucao


@app.get("/fonte/novidades", response_model=Novidades)
def verificar_novidades() -> dict:
    """Compara os meses-alvo com o controle, sem baixar valores."""
    try:
        return extracao.verificar_novidades()
    except (fonte.FonteIndisponivel, fonte.EstruturaAlterada):
        log.exception("Não foi possível consultar a fonte")
        raise HTTPException(status_code=503, detail="Fonte indisponível.") from None


@app.get("/health", responses={503: {"model": Saude}})
def saude(resposta: Response) -> Saude:
    """Só depende do banco: a fonte fora do ar não torna a API doente."""
    try:
        with banco.abrir() as conexao, conexao.cursor() as cursor:
            cursor.execute("SELECT 1")
    except psycopg2.Error:
        log.exception("Banco indisponível")
        resposta.status_code = 503
        return Saude(status="indisponivel")
    return Saude(status="ok")
