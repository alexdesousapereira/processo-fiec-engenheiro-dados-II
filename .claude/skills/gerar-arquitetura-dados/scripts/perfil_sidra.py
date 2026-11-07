"""Mede a estrutura e a qualidade de uma tabela do SIDRA antes do desenho da arquitetura.

Uso: python perfil_sidra.py --saida perfil.json [--tabela 8888] [--ano 2025]

Somente leitura da API pública do IBGE. As requisições são feitas por competência porque a
consulta com todos os períodos é recusada pela API (HTTP 400 na tabela 8888).
Supõe a dimensão D4 como classificação, como na tabela 8888; ajuste para outras tabelas.
"""
import argparse
import collections
import gzip
import json
import re
import time
import urllib.request

AGREGADOS = "https://servicodados.ibge.gov.br/api/v3/agregados"
VALORES = "https://apisidra.ibge.gov.br/values"
NUMERO = re.compile(r"-?\d+(\.\d+)?")
ATIVIDADE_TRANSFORMACAO = re.compile(r"^3\.\d+ ")


def buscar(url, tentativas=3):
    erro = None
    for tentativa in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "perfil-sidra/1.0"})
            with urllib.request.urlopen(req, timeout=180) as resposta:
                corpo = resposta.read()
            # A API de agregados responde em gzip mesmo sem Accept-Encoding
            if corpo[:2] == b"\x1f\x8b":
                corpo = gzip.decompress(corpo)
            return json.loads(corpo)
        except OSError as exc:
            erro = exc
            time.sleep(3 * (tentativa + 1))
    raise RuntimeError(f"Falha em {url}: {erro}")


def eh_numero(valor):
    return bool(NUMERO.fullmatch(valor))


def nao_numericos(linhas):
    return dict(collections.Counter(l["V"] for l in linhas if not eh_numero(l["V"])))


def perfilar(tabela, ano):
    meta = buscar(f"{AGREGADOS}/{tabela}/metadados")
    periodos = buscar(f"{AGREGADOS}/{tabela}/periodos")
    variaveis = meta["variaveis"]
    categorias = meta["classificacoes"][0]["categorias"]
    classificacao = meta["classificacoes"][0]["id"]
    indice = variaveis[0]["id"]

    primeiro, ultimo = periodos[0]["id"], periodos[-1]["id"]
    amostra = buscar(
        f"{VALORES}/t/{tabela}/n1/all/n2/all/n3/all/v/all/p/{ultimo}/c{classificacao}/all/f/a"
    )[1:]
    territorios = collections.defaultdict(set)
    for linha in amostra:
        territorios[linha["NN"]].add(linha["D1N"])

    linhas_ano = []
    for mes in range(1, 13):
        linhas_ano += buscar(
            f"{VALORES}/t/{tabela}/n3/all/v/{indice}/p/{ano}{mes:02d}/c{classificacao}/all/f/a"
        )[1:]
        time.sleep(0.3)

    atividades = [l for l in linhas_ano if ATIVIDADE_TRANSFORMACAO.match(l["D4N"])]
    validas = [l for l in atividades if eh_numero(l["V"])]

    por_uf_mes = collections.defaultdict(set)
    meses_por_par = collections.Counter()
    for linha in validas:
        por_uf_mes[(linha["D1N"], linha["D3C"])].add(linha["D4C"])
        meses_por_par[(linha["D1N"], linha["D4C"])] += 1
    por_uf = collections.defaultdict(set)
    for (uf, _), codigos in por_uf_mes.items():
        por_uf[uf] |= codigos

    chaves = collections.Counter((l["D1C"], l["D3C"], l["D4C"]) for l in linhas_ano)
    empates_top4 = []
    grupos = collections.defaultdict(list)
    for linha in validas:
        grupos[(linha["D1N"], linha["D3C"])].append(float(linha["V"]))
    for chave, valores in grupos.items():
        topo = sorted(valores, reverse=True)[:4]
        if len(set(topo)) < len(topo):
            empates_top4.append(f"{chave[0]}|{chave[1]}|{topo}")

    historico = buscar(
        f"{VALORES}/t/{tabela}/n3/all/v/{indice}/p/{primeiro}/c{classificacao}/all/f/a"
    )[1:]
    historico_ativ = [l for l in historico if ATIVIDADE_TRANSFORMACAO.match(l["D4N"])]
    historico_validas = [l for l in historico_ativ if eh_numero(l["V"])]

    return {
        "tabela": tabela,
        "nome": meta["nome"],
        "ultima_modificacao": periodos[-1].get("modificacao"),
        "periodos": {"qtde": len(periodos), "primeiro": primeiro, "ultimo": ultimo},
        "variaveis": [{"id": v["id"], "nome": v["nome"]} for v in variaveis],
        "qtde_categorias": len(categorias),
        "linhas_por_competencia_todos_niveis": len(amostra),
        "estimativa_linhas_total": len(amostra) * len(periodos),
        "territorios": {k: sorted(v) for k, v in territorios.items()},
        "nao_numericos_ultima_competencia": nao_numericos(amostra),
        "ano": {
            "ano": ano,
            "linhas_indice_ufs": len(linhas_ano),
            "meses": sorted({l["D3C"] for l in linhas_ano}),
            "nao_numericos": nao_numericos(linhas_ano),
            "chaves_duplicadas": sum(1 for v in chaves.values() if v > 1),
            "codigos_transformacao": len({l["D4C"] for l in atividades}),
            "linhas_transformacao": len(atividades),
            "linhas_transformacao_validas": len(validas),
            "atividades_validas_por_uf": {k: len(v) for k, v in sorted(por_uf.items())},
            "uf_mes_com_menos_de_3_atividades": [
                f"{k[0]}|{k[1]}|{len(v)}" for k, v in por_uf_mes.items() if len(v) < 3
            ],
            "pares_uf_atividade_validos": len(meses_por_par),
            "pares_uf_atividade_incompletos_no_ano": sum(
                1 for v in meses_por_par.values() if v != 12
            ),
            "empates_top4": empates_top4,
            "min_max": [min(float(l["V"]) for l in validas), max(float(l["V"]) for l in validas)],
        },
        "primeira_competencia": {
            "periodo": primeiro,
            "ufs": sorted({l["D1N"] for l in historico}),
            "linhas_transformacao": len(historico_ativ),
            "linhas_transformacao_validas": len(historico_validas),
            "nao_numericos": nao_numericos(historico),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", required=True)
    parser.add_argument("--tabela", type=int, default=8888)
    parser.add_argument("--ano", type=int, default=2025)
    args = parser.parse_args()
    with open(args.saida, "w", encoding="utf-8") as arquivo:
        json.dump(perfilar(args.tabela, args.ano), arquivo, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
