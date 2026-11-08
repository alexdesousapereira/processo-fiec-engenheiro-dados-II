"""Confere o mockup contra o warehouse e contra as regras de SVG do pbi-mockup.

Uso, na imagem da ingestão, com a pasta montada:
    docker compose run --rm -v "$(pwd)/mockup:/app/mockup" ingestao python /app/mockup/conferir_mockup.py

Termina com código 1 se algum número das telas divergir do warehouse ou se um SVG quebrar as regras.
"""
import logging
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal
from pathlib import Path

from pim_pf import banco

log = logging.getLogger("conferir_mockup")
PASTA = Path(__file__).resolve().parent
TELAS = [PASTA / "tela-01-capa.svg", PASTA / "tela-02-analise.svg"]
TELA_COM_NUMEROS = PASTA / "tela-02-analise.svg"
NS = "{http://www.w3.org/2000/svg}"
ALVOS_DE_URL = {"linearGradient", "radialGradient", "clipPath", "pattern", "mask", "filter"}


def numero(valor: Decimal | float) -> str:
    """145.034 vira "145,03", no padrão brasileiro."""
    return f"{Decimal(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def com_sinal(valor: Decimal | float) -> str:
    return ("+" if valor >= 0 else "-") + numero(abs(Decimal(valor)))


def consultas() -> dict[str, list[tuple]]:
    """Executa cada consulta de dados-referencia.sql, identificada pelo comentário '-- nome:'."""
    texto = (PASTA / "dados-referencia.sql").read_text(encoding="utf-8")
    resultados = {}
    with banco.abrir() as conexao, conexao.cursor() as cursor:
        for nome, sql in re.findall(r"-- nome: (\w+)\n(.*?;)", texto, flags=re.S):
            cursor.execute(sql)
            resultados[nome] = cursor.fetchall()
    return resultados


def valores_esperados(dados: dict[str, list[tuple]]) -> tuple[list[str], set[str]]:
    """Devolve os valores que a tela precisa mostrar e todos os valores que ela pode mostrar.

    A linha mensal só rotula o mês selecionado (janeiro) e o pico; os demais meses ficam no eixo.
    """
    atividades = dados["atividades"]
    mensal = dados["media_mensal"]
    acima = sum(1 for _, _, _, diferenca, _ in atividades if diferenca > 0)
    atualizado: date = dados["atualizacao"][0][0]
    pico = max(mensal, key=lambda linha: linha[1])
    obrigatorios = [numero(atividades[0][4]), f"{len(atividades)} atividades", f"{acima} de {len(atividades)}",
                    atualizado.strftime("%d/%m/%Y"), numero(mensal[0][1]), numero(pico[1])]
    for _, _, indice, diferenca, _ in atividades:
        obrigatorios += [numero(indice), com_sinal(diferenca)]
    permitidos = set(obrigatorios) | {numero(media) for _, media in mensal}
    return obrigatorios, permitidos


def decimais_exibidos(texto: str) -> set[str]:
    """Todo número com vírgula decimal que aparece na tela, com o sinal quando houver."""
    return set(re.findall(r"[+-]?\d{1,3}(?:\.\d{3})*,\d{2}", texto))


def textos(arquivo: Path) -> str:
    """Todo o texto visível da tela, com o sinal de menos tipográfico normalizado."""
    raiz = ET.parse(arquivo).getroot()
    partes = ["".join(t.itertext()) for t in raiz.iter(f"{NS}text")]
    return "\n".join(partes).replace("−", "-")


def problemas_de_estrutura(arquivo: Path) -> list[str]:
    """Regras do pbi-mockup para o SVG abrir certo no Figma e no navegador."""
    problemas = []
    bruto = arquivo.read_text(encoding="utf-8")
    raiz = ET.fromstring(bruto)
    por_id = {e.get("id"): e.tag.replace(NS, "") for e in raiz.iter() if e.get("id")}
    for proibido in ("use", "symbol"):
        if raiz.find(f".//{NS}{proibido}") is not None:
            problemas.append(f"usa <{proibido}>")
    if "currentColor" in bruto:
        problemas.append("usa currentColor")
    for alvo in re.findall(r"url\(#([^)]+)\)", bruto):
        if por_id.get(alvo) not in ALVOS_DE_URL:
            problemas.append(f"url(#{alvo}) não aponta para um gradiente ou recorte")
    return problemas


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    faltando = [t.name for t in TELAS if not t.exists()]
    if faltando:
        log.error("Telas ausentes: %s", faltando)
        return 1

    falhas = 0
    for tela in TELAS:
        try:
            problemas = problemas_de_estrutura(tela)
        except ET.ParseError as erro:
            problemas = [f"XML mal formado: {erro}"]
        for problema in problemas:
            log.error("%s: %s", tela.name, problema)
        falhas += len(problemas)

    texto = textos(TELA_COM_NUMEROS)
    obrigatorios, permitidos = valores_esperados(consultas())
    ausentes = [valor for valor in obrigatorios if valor not in texto]
    for valor in ausentes:
        log.error("%s: valor do warehouse ausente: %s", TELA_COM_NUMEROS.name, valor)
    # Sinal à parte, todo decimal exibido precisa existir no warehouse: nenhum número inventado.
    sem_sinal = {p.lstrip("+-") for p in permitidos}
    estranhos = sorted(v for v in decimais_exibidos(texto) if v not in permitidos and v.lstrip("+-") not in sem_sinal)
    for valor in estranhos:
        log.error("%s: número que não existe no warehouse: %s", TELA_COM_NUMEROS.name, valor)
    falhas += len(ausentes) + len(estranhos)

    log.info("%d valores obrigatórios conferidos, %d ausentes, %d sem origem no warehouse, %d problemas de estrutura.",
             len(obrigatorios), len(ausentes), len(estranhos), falhas - len(ausentes) - len(estranhos))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
