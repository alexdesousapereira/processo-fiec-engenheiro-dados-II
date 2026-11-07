"""Leva os dados dos arquivos brutos até a Stage. Daí em diante, quem carrega é o dbt."""
import argparse
import io
import logging
import uuid
from datetime import datetime, timezone

import pandas as pd
from psycopg2.extensions import cursor as Cursor

from pim_pf import banco, extracao, tratamento

log = logging.getLogger(__name__)


def quadro_variaveis(metadados: dict) -> pd.DataFrame:
    return pd.DataFrame(metadados["variaveis"])


def quadro_categorias(metadados: dict) -> pd.DataFrame:
    return pd.DataFrame(metadados["classificacoes"][0]["categorias"])


def quadro_territorio(localidades: dict[str, list[dict]]) -> pd.DataFrame:
    """Junta os três níveis. Cada item traz o nível dentro de um objeto, como {"id": "N3"}."""
    itens = [item for nivel in localidades.values() for item in nivel]
    return pd.DataFrame(
        {"id": [i["id"] for i in itens], "nome": [i["nome"] for i in itens], "nivel": [i["nivel"]["id"] for i in itens]}
    )


# Nomes de tabela só vêm destas constantes: nunca de um valor externo.
# Cada dimensão indica o arquivo de origem, como o JSON vira DataFrame e como ela é tratada.
DIMENSOES = {
    "variaveis": ("metadados", quadro_variaveis, tratamento.tratar_variaveis),
    "categoria": ("metadados", quadro_categorias, tratamento.tratar_categorias),
    "territorio": ("localidades", quadro_territorio, tratamento.tratar_territorio),
}
PRODUCAO = extracao.PRODUCAO
TABELAS = (*DIMENSOES, PRODUCAO)


def _ler_pendentes(cursor: Cursor) -> pd.DataFrame:
    """Lê a versão mais recente de cada mês pendente e anexa execução e origem."""
    cursor.execute(
        "SELECT periodo, arquivo, execucao_id FROM controle.carga_periodo "
        "WHERE carregado_em IS NULL ORDER BY periodo"
    )
    partes = []
    for _, arquivo, execucao_id in cursor.fetchall():
        parte = tratamento.tratar(pd.DataFrame(extracao.ler_arquivo(arquivo)))
        parte["execucao_id"], parte["path_origem"] = execucao_id, arquivo
        partes.append(parte)
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


def _preparar_dimensao(cursor: Cursor, tabela: str, momento: datetime) -> pd.DataFrame:
    recurso, para_quadro, tratar = DIMENSOES[tabela]
    dados, arquivo = extracao.ler_recurso(cursor, recurso)
    return tratar(para_quadro(dados)).assign(path_origem=arquivo, data_carga=momento)


def _copiar(cursor: Cursor, tabela: str, df: pd.DataFrame) -> None:
    """COPY é a forma mais rápida de carregar muitas linhas no PostgreSQL."""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False, na_rep="")
    buffer.seek(0)
    colunas = ", ".join(df.columns)
    cursor.copy_expert(f"COPY stage.{tabela} ({colunas}) FROM STDIN WITH (FORMAT csv)", buffer)


def carregar_stage(cursor: Cursor, tabela: str, momento: datetime) -> dict:
    """Trata primeiro e só depois toca na Stage, para um dado inválido não apagar nada."""
    dimensoes = list(DIMENSOES) if tabela == PRODUCAO else [tabela]
    tabelas = {nome: _preparar_dimensao(cursor, nome, momento) for nome in dimensoes}
    nulos, meses = {}, []
    if tabela == PRODUCAO:
        producao = _ler_pendentes(cursor)
        if not producao.empty:
            producao = tratamento.tabela_producao(producao.assign(data_carga=momento))
            nulos[PRODUCAO] = int(producao["valor"].isna().sum())
            meses = sorted(producao["periodo"].unique().tolist())
        tabelas[PRODUCAO] = producao
        log.info("Meses carregados na Stage: %s", meses)

    for nome, dados in tabelas.items():
        cursor.execute(f"TRUNCATE stage.{nome}")
        if not dados.empty:
            _copiar(cursor, nome, dados)
        log.info("stage.%s: %d linhas", nome, len(dados))
    return {"linhas": {nome: len(dados) for nome, dados in tabelas.items()}, "nulos": nulos, "meses": meses}


def executar_extracao(tabela: str, modo: str, inicio: int | None, fim: int | None, execucao_id: str) -> dict:
    """Atualiza os arquivos brutos, valida, trata e recarrega a Stage da tabela pedida."""
    if tabela not in TABELAS:
        raise ValueError(f"Tabela desconhecida: {tabela}")
    with banco.abrir() as conexao, conexao.cursor() as cursor:
        contagem = extracao.atualizar_brutos(conexao, cursor, tabela, modo, inicio, fim, execucao_id)
        if tabela == PRODUCAO:
            extracao.validar_brutos(cursor)
        stage = carregar_stage(cursor, tabela, datetime.now(timezone.utc))
        cursor.execute("SELECT periodo FROM controle.carga_periodo WHERE NOT completo ORDER BY periodo")
        parciais = [periodo for periodo, in cursor.fetchall()]
    resumo = {
        "periodos_gravados": contagem["gravados"],
        "periodos_sem_mudanca": contagem["sem_mudanca"],
        "periodos_parciais": parciais,
        "meses_gravados": contagem["meses_gravados"],
        "meses_stage": stage["meses"],
        "linhas_stage": stage["linhas"],
        "nulos_stage": stage["nulos"],
    }
    log.info("Execução %s (%s, %s): %s", execucao_id, tabela, modo, resumo)
    return resumo


def main() -> None:
    """Executa a extração sem a API, para diagnóstico e para validar a Stage."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    argumentos = argparse.ArgumentParser(description=main.__doc__)
    argumentos.add_argument("tabela", choices=TABELAS)
    argumentos.add_argument("--modo", choices=["auto", "completa", "reprocessar"], default="auto")
    argumentos.add_argument("--inicio", help="Primeiro mês, como 2025-01")
    argumentos.add_argument("--fim", help="Último mês, como 2025-03")
    pedido = argumentos.parse_args()

    if bool(pedido.inicio) != bool(pedido.fim):
        argumentos.error("Informe --inicio e --fim juntos")
    inicio = extracao.texto_para_periodo(pedido.inicio) if pedido.inicio else None
    fim = extracao.texto_para_periodo(pedido.fim) if pedido.fim else None
    if inicio is not None:
        extracao.validar_intervalo(inicio, fim)
    executar_extracao(pedido.tabela, pedido.modo, inicio, fim, f"manual-{uuid.uuid4()}")


if __name__ == "__main__":
    main()
