"""Ingestão (I1 a I10): escolhe os meses, detecta o que mudou e guarda as respostas originais."""
import gzip
import hashlib
import json
import logging
import os
import re
import time
from collections.abc import Iterable
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from psycopg2.extensions import connection
from psycopg2.extensions import cursor as Cursor

from pim_pf import banco, fonte

log = logging.getLogger(__name__)
PAUSA_ENTRE_REQUISICOES = 0.2
NIVEL_UF = "3"
JANELA_MESES = 3
MAXIMO_MESES_NO_INTERVALO = 24

PRODUCAO = "producao_fisica"
RECURSOS_POR_TABELA = {
    "variaveis": ["metadados"],
    "categoria": ["metadados"],
    "territorio": ["localidades"],
    # A produção carrega também as dimensões, para o fato não violar as chaves estrangeiras.
    PRODUCAO: ["metadados", "localidades"],
}
BUSCAS_DE_RECURSO = {
    "metadados": (fonte.buscar_metadados, fonte.URL_METADADOS),
    "localidades": (fonte.buscar_localidades, fonte.URL_LOCALIDADES.format(nivel="{N1,N2,N3}")),
}


class PeriodosIndisponiveis(Exception):
    """Foram pedidos meses que a fonte não tem."""


class SemDadoBruto(Exception):
    """O reprocessamento precisa de um arquivo que não foi guardado."""


def texto_para_periodo(texto: str) -> int:
    """'2025-03' vira 202503, o formato usado pela fonte e pelo banco."""
    return int(texto.replace("-", ""))


def meses_do_intervalo(inicio: int, fim: int) -> list[int]:
    meses = []
    ano, mes = inicio // 100, inicio % 100
    while ano * 100 + mes <= fim:
        meses.append(ano * 100 + mes)
        ano, mes = (ano + 1, 1) if mes == 12 else (ano, mes + 1)
    return meses


def validar_intervalo(inicio: int, fim: int) -> None:
    if inicio > fim:
        raise ValueError("inicio não pode ser depois de fim")
    if len(meses_do_intervalo(inicio, fim)) > MAXIMO_MESES_NO_INTERVALO:
        raise ValueError(f"O intervalo aceita no máximo {MAXIMO_MESES_NO_INTERVALO} meses")


def periodos_alvo(
    na_fonte: Iterable[int], controle: dict[int, dict], modo: str, inicio: int | None = None, fim: int | None = None
) -> list[int]:
    """Decide quais meses consultar na fonte.

    Sem intervalo, une os meses ainda não extraídos, os 3 últimos publicados e os parciais.
    A mesma regra cobre a primeira carga, uma carga interrompida e um mês novo, sem um caso
    especial de "primeira vez". Revisões mais antigas que a janela exigem o modo `completa`.
    """
    publicados = sorted(na_fonte)
    if modo == "completa":
        return publicados
    if inicio is not None and fim is not None:
        pedidos = meses_do_intervalo(inicio, fim)
        faltantes = sorted(set(pedidos) - set(publicados))
        if faltantes:
            raise PeriodosIndisponiveis(f"Meses que a fonte não tem: {faltantes}")
        return pedidos
    ausentes = set(publicados) - set(controle)
    parciais = {p for p in publicados if p in controle and not controle[p]["completo"]}
    return sorted(ausentes | parciais | set(publicados[-JANELA_MESES:]))


def periodos_com_novidade(na_fonte: dict[int, date], no_controle: dict[int, date]) -> list[int]:
    """Meses novos ou cuja data na fonte difere da registrada.

    A fonte informa a mesma data para todos os meses, então isso só diz que algo mudou.
    Quem descobre o que mudou é o hash. Comparar mês a mês cobre extrações interrompidas.
    """
    return sorted(p for p, data in na_fonte.items() if no_controle.get(p) != data)


def calcular_novidades(na_fonte: dict[int, date], controle: dict[int, dict]) -> dict:
    """Compara só os meses-alvo: os antigos, fora da janela, nunca têm a data atualizada."""
    alvos = periodos_alvo(na_fonte, controle, "auto")
    alterados = periodos_com_novidade(
        {p: na_fonte[p] for p in alvos},
        {p: c["data_fonte"] for p, c in controle.items()},
    )
    pendentes = sorted(p for p, c in controle.items() if c["carregado_em"] is None)
    return {"ha_novidade": bool(alterados or pendentes), "meses_alterados": alterados, "meses_pendentes": pendentes}


def calcular_hash(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def resumir_conteudo(linhas: list[dict]) -> dict:
    """Mede o mês. Sem números nas UFs, ele está parcial, como 202609 na medição."""
    def eh_numero(valor: str) -> bool:
        return re.fullmatch(r"-?\d+(\.\d+)?", valor) is not None

    numericas = [r for r in linhas if eh_numero(r["V"])]
    numericas_uf = [r for r in numericas if r["NC"] == NIVEL_UF]
    return {
        "linhas": len(linhas),
        "linhas_numericas": len(numericas),
        "linhas_uf_numericas": len(numericas_uf),
        "completo": len(numericas_uf) > 0,
    }


def caminho_ingestao(raiz: Path, periodo: int, momento: datetime) -> Path:
    """I5 e I6: organiza por mês e versão de ingestão."""
    return raiz / "sidra" / "tabela=8888" / f"periodo={periodo}" / f"ingestao={momento:%Y%m%dT%H%M%S}"


def caminho_recurso(raiz: Path, recurso: str, momento: datetime) -> Path:
    return raiz / "sidra" / "tabela=8888" / recurso / f"ingestao={momento:%Y%m%dT%H%M%S}"


def gravar_bruto(pasta: Path, conteudo: bytes, manifesto: dict) -> Path:
    """Escreve em uma pasta nova. Versões anteriores nunca são alteradas."""
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / "dados.json.gz"
    # mtime=0 faz o mesmo conteúdo gerar sempre o mesmo arquivo compactado.
    with open(arquivo, "wb") as destino, gzip.GzipFile(fileobj=destino, mode="wb", mtime=0) as compactado:
        compactado.write(conteudo)
    (pasta / "manifesto.json").write_text(json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")
    return arquivo


def ler_arquivo(arquivo: str) -> dict | list:
    with gzip.open(arquivo, "rt", encoding="utf-8") as origem:
        return json.load(origem)


def ler_controle(cursor: Cursor) -> dict[int, dict]:
    cursor.execute(
        "SELECT periodo, data_fonte, hash_conteudo, carregado_em, completo, arquivo FROM controle.carga_periodo"
    )
    return {
        p: {"data_fonte": d, "hash": h, "carregado_em": c, "completo": ok, "arquivo": a}
        for p, d, h, c, ok, a in cursor.fetchall()
    }


def verificar_novidades() -> dict:
    """Só lê a lista de períodos e o controle. Não baixa valores."""
    with fonte.criar_sessao() as sessao:
        na_fonte = fonte.buscar_periodos(sessao)
    with banco.abrir() as conexao, conexao.cursor() as cursor:
        resultado = calcular_novidades(na_fonte, ler_controle(cursor))
    log.info(
        "Meses alterados: %s. Pendentes de carga: %s.",
        resultado["meses_alterados"], resultado["meses_pendentes"],
    )
    return resultado


def codigos_do_recurso(recurso: str, dados: dict) -> set[str]:
    """Códigos que definem a estrutura da fonte. Mudar um nome não muda a estrutura."""
    if recurso == "localidades":
        return {f"território {item['id']}" for itens in dados.values() for item in itens}
    return {f"variável {v['id']}" for v in dados["variaveis"]} | {
        f"categoria {c['id']}" for c in dados["classificacoes"][0]["categorias"]
    }


def gravar_recurso(
    cursor: Cursor, raiz: Path, recurso: str, conteudo: bytes, url: str, execucao_id: str,
    aceitar_mudanca: bool = False,
) -> None:
    """Guarda metadados ou localidades, criando uma pasta nova só quando o conteúdo muda.

    Código novo ou removido interrompe a carga, para alguém avaliar a mudança na fonte. Quem
    a aceita é o modo `completa`, que também atualiza o histórico com a nova estrutura.
    """
    hash_atual = calcular_hash(conteudo)
    cursor.execute("SELECT hash_conteudo, arquivo FROM controle.carga_recurso WHERE recurso = %s", (recurso,))
    registro = cursor.fetchone()
    if registro and registro[0] == hash_atual:
        return
    if registro and not aceitar_mudanca and Path(registro[1]).exists():
        diferenca = codigos_do_recurso(recurso, ler_arquivo(registro[1])) ^ codigos_do_recurso(
            recurso, json.loads(conteudo)
        )
        if diferenca:
            raise fonte.EstruturaAlterada(
                f"A fonte mudou em {recurso}: {sorted(diferenca)}. Para aceitar, execute o modo completa."
            )

    momento = datetime.now(timezone.utc)
    manifesto = {
        "url": url,
        "recurso": recurso,
        "ingestao_em": momento.isoformat(),
        "execucao_id": execucao_id,
        "hash_sha256": hash_atual,
    }
    arquivo = gravar_bruto(caminho_recurso(raiz, recurso, momento), conteudo, manifesto)
    cursor.execute(
        """
        INSERT INTO controle.carga_recurso (recurso, hash_conteudo, arquivo, execucao_id, ingestao_em)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (recurso) DO UPDATE SET
            hash_conteudo = EXCLUDED.hash_conteudo, arquivo = EXCLUDED.arquivo,
            execucao_id = EXCLUDED.execucao_id, ingestao_em = EXCLUDED.ingestao_em
        """,
        (recurso, hash_atual, str(arquivo), execucao_id, momento),
    )


def ler_recurso(cursor: Cursor, recurso: str) -> tuple[dict, str]:
    """Lê a última versão guardada. Devolve o conteúdo e o caminho do arquivo."""
    cursor.execute("SELECT arquivo FROM controle.carga_recurso WHERE recurso = %s", (recurso,))
    registro = cursor.fetchone()
    if not registro or not Path(registro[0]).exists():
        raise SemDadoBruto(f"Não há arquivo guardado de {recurso}")
    return ler_arquivo(registro[0]), registro[0]


def extrair_periodos(
    sessao: requests.Session, conexao: connection, cursor: Cursor, raiz: Path, na_fonte: dict[int, date], controle: dict[int, dict],
    alvos: list[int], modo: str, execucao_id: str,
) -> dict:
    """Lê a fonte e grava apenas os meses cujo conteúdo mudou. No modo `completa`, regrava todos."""
    gravados, sem_mudanca = [], []
    for periodo in alvos:
        conteudo = fonte.buscar_valores(sessao, periodo)
        time.sleep(PAUSA_ENTRE_REQUISICOES)
        hash_atual = calcular_hash(conteudo)
        registro = controle.get(periodo)
        if modo == "auto" and registro and registro["hash"] == hash_atual:
            cursor.execute(
                "UPDATE controle.carga_periodo SET data_fonte = %s WHERE periodo = %s",
                (na_fonte[periodo], periodo),
            )
            sem_mudanca.append(periodo)
        else:
            _gravar_periodo(cursor, raiz, periodo, conteudo, hash_atual, na_fonte[periodo], execucao_id)
            gravados.append(periodo)
        # Confirma mês a mês: uma falha no meio não perde o que já foi extraído.
        conexao.commit()
    log.info("Extração: meses gravados %s; meses sem mudança %s.", gravados, sem_mudanca)
    return {"gravados": len(gravados), "sem_mudanca": len(sem_mudanca), "meses_gravados": gravados}


def _gravar_periodo(
    cursor: Cursor, raiz: Path, periodo: int, conteudo: bytes, hash_atual: str, data_fonte: date, execucao_id: str
) -> None:
    momento = datetime.now(timezone.utc)
    try:
        resumo = resumir_conteudo(json.loads(conteudo))
    except (ValueError, KeyError, TypeError) as erro:
        raise fonte.EstruturaAlterada(f"Resposta inesperada no mês {periodo}: {erro!r}") from erro
    manifesto = {  # I7 e I8: origem e data da ingestão
        "url": fonte.url_valores(periodo),
        "periodo": periodo,
        "data_fonte": data_fonte.isoformat(),
        "ingestao_em": momento.isoformat(),
        "execucao_id": execucao_id,
        "hash_sha256": hash_atual,
        **resumo,
    }
    arquivo = gravar_bruto(caminho_ingestao(raiz, periodo, momento), conteudo, manifesto)
    cursor.execute(
        """
        INSERT INTO controle.carga_periodo
            (periodo, data_fonte, hash_conteudo, arquivo, linhas, linhas_numericas,
             linhas_uf_numericas, completo, execucao_id, ingestao_em, carregado_em)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
        ON CONFLICT (periodo) DO UPDATE SET
            data_fonte = EXCLUDED.data_fonte, hash_conteudo = EXCLUDED.hash_conteudo,
            arquivo = EXCLUDED.arquivo, linhas = EXCLUDED.linhas,
            linhas_numericas = EXCLUDED.linhas_numericas,
            linhas_uf_numericas = EXCLUDED.linhas_uf_numericas, completo = EXCLUDED.completo,
            execucao_id = EXCLUDED.execucao_id, ingestao_em = EXCLUDED.ingestao_em,
            carregado_em = NULL
        """,
        (periodo, data_fonte, hash_atual, str(arquivo), resumo["linhas"], resumo["linhas_numericas"],
         resumo["linhas_uf_numericas"], resumo["completo"], execucao_id, momento),
    )


def marcar_para_reprocessar(cursor: Cursor, controle: dict[int, dict], inicio: int | None, fim: int | None) -> list[int]:
    """Faz os meses voltarem ao warehouse a partir dos arquivos guardados, sem acessar a fonte."""
    alvos = meses_do_intervalo(inicio, fim) if inicio is not None and fim is not None else sorted(controle)
    faltantes = [p for p in alvos if p not in controle or not Path(controle[p]["arquivo"]).exists()]
    if not alvos or faltantes:
        raise SemDadoBruto(f"Meses sem arquivo guardado: {faltantes or 'nenhuma carga anterior'}")
    cursor.execute("UPDATE controle.carga_periodo SET carregado_em = NULL WHERE periodo = ANY(%s)", (alvos,))
    log.info("Reprocessamento sem acessar a fonte: meses %s.", alvos)
    return alvos


def checar_mes(linhas: list[dict], metadados: dict, localidades: dict[str, list[dict]]) -> list[str]:
    """Compara um mês com os metadados e as localidades da fonte e devolve os problemas encontrados."""
    problemas = []
    variaveis = {r["D2C"] for r in linhas}
    categorias = {r["D4C"] for r in linhas}
    territorios = {r["D1C"] for r in linhas}

    esperadas_var = {str(v["id"]) for v in metadados["variaveis"]}
    esperadas_cat = {str(c["id"]) for c in metadados["classificacoes"][0]["categorias"]}
    if variaveis != esperadas_var:
        problemas.append(f"variáveis diferentes dos metadados: {sorted(variaveis ^ esperadas_var)}")
    if categorias != esperadas_cat:
        problemas.append(f"categorias diferentes dos metadados: {sorted(categorias ^ esperadas_cat)}")
    esperados_ter = {str(item["id"]) for itens in localidades.values() for item in itens}
    if territorios != esperados_ter:
        problemas.append(f"territórios diferentes das localidades: {sorted(territorios ^ esperados_ter)}")

    esperado = len(territorios) * len(esperadas_var) * len(esperadas_cat)
    if len(linhas) != esperado:
        problemas.append(f"{len(linhas)} linhas recebidas, {esperado} esperadas")
    return problemas


def validar_brutos(cursor: Cursor) -> None:
    """Falha cedo se a fonte mudou de estrutura, antes de tratar os dados.

    Compara com as versões guardadas, para o reprocessamento não depender da fonte.
    """
    metadados, _ = ler_recurso(cursor, "metadados")
    localidades, _ = ler_recurso(cursor, "localidades")
    cursor.execute("SELECT periodo, arquivo FROM controle.carga_periodo WHERE carregado_em IS NULL")
    pendentes = cursor.fetchall()

    falhas = {}
    for periodo, arquivo in pendentes:
        problemas = checar_mes(ler_arquivo(arquivo), metadados, localidades)
        if problemas:
            falhas[periodo] = problemas
    if falhas:
        raise fonte.EstruturaAlterada(f"Arquivos brutos reprovados: {falhas}")
    log.info("Arquivos brutos validados: meses %s.", [periodo for periodo, _ in pendentes])


def atualizar_brutos(
    conexao: connection, cursor: Cursor, tabela: str, modo: str, inicio: int | None, fim: int | None, execucao_id: str
) -> dict:
    """Atualiza os arquivos brutos que a tabela pedida usa e devolve a contagem de meses."""
    if modo == "reprocessar":
        if tabela == PRODUCAO:
            marcar_para_reprocessar(cursor, ler_controle(cursor), inicio, fim)
        return {"gravados": 0, "sem_mudanca": 0, "meses_gravados": []}

    raiz = Path(os.environ["PIM_DIR_BRUTOS"])
    with fonte.criar_sessao() as sessao:
        for recurso in RECURSOS_POR_TABELA[tabela]:
            buscar, url = BUSCAS_DE_RECURSO[recurso]
            gravar_recurso(cursor, raiz, recurso, buscar(sessao), url, execucao_id, modo == "completa")
        conexao.commit()
        if tabela != PRODUCAO:
            return {"gravados": 0, "sem_mudanca": 0, "meses_gravados": []}

        na_fonte = fonte.buscar_periodos(sessao)
        controle = ler_controle(cursor)
        alvos = periodos_alvo(na_fonte, controle, modo, inicio, fim)
        return extrair_periodos(sessao, conexao, cursor, raiz, na_fonte, controle, alvos, modo, execucao_id)
