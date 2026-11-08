"""Gera as duas telas do mockup a partir do warehouse, seguindo as regras de requisitos/pbi-mockup.

A geometria vem do esqueleto canvas-topo-marca e dos componentes grafico-01-barras e grafico-02-linha.
Os ícones são do Google Material Symbols, copiados como caminhos. Os números saem de dados-referencia.sql.

Uso, na imagem da ingestão:
    docker compose run --rm -v "$(pwd)/mockup:/app/mockup" ingestao python /app/mockup/ferramentas/gerar_telas.py
"""
import base64
import logging
import math
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conferir_mockup import com_sinal, consultas, numero  # noqa: E402

log = logging.getLogger("gerar_telas")
PASTA = Path(__file__).resolve().parents[1]

# Tokens: cor de ação do tema do Observatório; neutros do pbi-mockup, com #5C6470 em todo texto pequeno (contraste ≥ 4,5:1).
ACAO, INK, INK2 = "#0E4194", "#33394C", "#5C6470"
NEUTRO, LINHA, BORDA, FUNDO, GRADE, BRANCO = "#C9CDD4", "#7C8595", "#E6E8EC", "#F5F7FB", "#EDEFF2", "#FFFFFF"
FONTE = "'Segoe UI',system-ui,Inter,sans-serif"
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
         "novembro", "dezembro"]
ICONES = {
    "ranking": "M160-200h160v-320H160v320Zm240 0h160v-560H400v560Zm240 0h160v-240H640v240ZM80-120v-480h240v-240h320v320h240v400H80Z",
    "functions": "M240-160v-80l260-240-260-240v-80h480v120H431l215 200-215 200h289v120H240Z",
    "trend-up": "m136-240-56-56 296-298 160 160 208-206H640v-80h240v240h-80v-104L536-320 376-480 136-240Z",
    "factory": "M80-80v-481l280-119v80l200-80v120h320v480H80Zm80-80h640v-320H480v-82l-200 80v-78l-120 53v347Zm280-80h80v-160h-80v160Zm-160 0h80v-160h-80v160Zm320 0h80v-160h-80v160Zm280-320H680l40-320h120l40 320ZM160-160h640-640Z",
}

# Grade de 12 colunas: margem 24, gutter 20, área útil de 1232.
COLUNA = (1232 - 11 * 20) / 12


def x_coluna(coluna: int) -> float:
    return round(24 + coluna * (COLUNA + 20), 2)


def largura(colunas: int) -> float:
    return round(colunas * COLUNA + (colunas - 1) * 20, 2)


def texto(x: float, y: float, conteudo: str, tamanho: int, cor: str, peso: int | None = None,
          ancora: str | None = None, espacamento: float | None = None) -> str:
    extras = (f' font-weight="{peso}"' if peso else "") + (f' text-anchor="{ancora}"' if ancora else "")
    extras += f' letter-spacing="{espacamento}"' if espacamento else ""
    return f'<text x="{x:g}" y="{y:g}" font-size="{tamanho}" fill="{cor}"{extras}>{escape(conteudo)}</text>'


def icone(nome: str, x: float, y: float, tamanho: float, cor: str) -> str:
    """Ícone como <path> com transform e cor fixa: abre igual no Figma e no navegador."""
    return (f'<g transform="translate({x:g},{y:g}) scale({tamanho / 960:.6f}) translate(0,960)" fill="{cor}">'
            f'<path d="{ICONES[nome]}"/></g>')


def logo() -> str:
    """Logo da FIEC (332 × 95 px) embutido como PNG: a tela abre sem arquivos externos."""
    dados = base64.b64encode((PASTA / "assets" / "logo-fiec.png").read_bytes()).decode("ascii")
    altura = 34
    largura_logo = round(332 * altura / 95, 1)
    return (f'<image x="24" y="13" width="{largura_logo}" height="{altura}" preserveAspectRatio="xMidYMid meet" '
            f'href="data:image/png;base64,{dados}"/>')


def menu(ativa: str) -> str:
    abas, x = [], 440
    for nome in ("Capa", "Análise"):
        if nome == ativa:
            abas.append(texto(x, 36, nome, 13, ACAO, 600))
            abas.append(f'<rect x="{x}" y="46" width="{round(len(nome) * 8.2)}" height="3" rx="1.5" fill="{ACAO}"/>')
        else:
            abas.append(texto(x, 36, nome, 13, INK2))
        x += 72
    return f"""<g id="menu">
    <rect x="0" y="0" width="1280" height="60" fill="{BRANCO}"/>
    <rect x="0" y="59" width="1280" height="1" fill="{BORDA}"/>
    {logo()}
    <rect x="160" y="16" width="1" height="28" fill="{BORDA}"/>
    {texto(176, 36, "Observatório da Indústria", 16, INK, 600)}
    {"".join(abas)}
  </g>"""


def cabecalho(titulo: str, referencia: str, atualizado: str) -> str:
    return f"""<g id="cabecalho">
    {texto(24, 98, titulo, 22, INK, 600)}
    <text x="24" y="118" font-size="13" fill="{INK2}">Dados: <tspan font-weight="600" fill="{INK}">{escape(referencia)}</tspan> · atualizado em {atualizado}</text>
  </g>"""


def rodape(atualizado: str) -> str:
    return f"""<g id="rodape">
    {texto(24, 690, "Fonte: IBGE, Pesquisa Industrial Mensal – Produção Física (PIM-PF), tabela 8888 do SIDRA", 11, INK2)}
    {texto(1256, 690, f"MOCKUP — números do warehouse em {atualizado}", 11, INK2, ancora="end")}
  </g>"""


def tela(titulo: str, corpo: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" '
            f'font-family="{FONTE}">\n  <title>{escape(titulo)}</title>\n'
            f'  <g id="fundo"><rect width="1280" height="720" fill="{FUNDO}"/></g>\n  {corpo}\n</svg>\n')


def cartao(indice: int, coluna: int, conteudo: str, icone_nome: str) -> str:
    return f"""<g id="kpi-{indice}" transform="translate({x_coluna(coluna):g},132)">
      <rect width="{largura(4):g}" height="88" rx="10" fill="{BRANCO}" stroke="{BORDA}"/>
      <rect x="16" y="16" width="36" height="36" rx="9" fill="{ACAO}" fill-opacity="0.12"/>
      {icone(icone_nome, 22, 22, 24, ACAO)}
      {conteudo}
    </g>"""


def rotulo_atividade(cnae: str, nome: str, limite: int = 34) -> str:
    """O eixo de categorias do Power BI corta nomes longos com reticências; o mockup faz o mesmo."""
    completo = f"{cnae} {nome}"
    return completo if len(completo) <= limite else completo[: limite - 1].rstrip() + "…"


def grafico_barras(atividades: list[tuple], media: Decimal) -> str:
    """grafico-01-barras: barras horizontais ordenadas, a partir do zero, top 3 na cor de ação."""
    largura_visual = largura(8)
    inicio, comprimento = 264, 390
    escala = comprimento / float(max(a[2] for a in atividades))
    lider = atividades[0]
    barras, rotulos = [], []
    for posicao, (cnae, nome, indice, diferenca, _) in enumerate(atividades):
        y = 84 + posicao * 28
        destaque = posicao < 3
        fim = inicio + float(indice) * escala
        rotulos.append(texto(256, y + 19, rotulo_atividade(cnae, nome), 12, INK2, ancora="end"))
        barras.append(f'<rect x="{inicio}" y="{y + 5}" width="{fim - inicio:.1f}" height="18" '
                      f'fill="{ACAO if destaque else NEUTRO}"/>')
        # O valor tem fundo branco próprio: a linha tracejada da média, desenhada antes, não o corta.
        valor = f"{numero(indice)} ({com_sinal(diferenca)})"
        largura_valor = len(valor) * 7.2
        rotulos.append(f'<rect x="{fim + 3:.1f}" y="{y + 6}" width="{largura_valor:.1f}" height="16" fill="{BRANCO}"/>')
        rotulos.append(texto(round(fim + 6, 1), y + 19, valor, 12, INK if destaque else INK2, 600 if destaque else None))
    x_media = round(inicio + float(media) * escala, 1)
    return f"""<g id="visual-principal" transform="translate({x_coluna(0):g},240)">
      <rect width="{largura_visual:g}" height="412" rx="10" fill="{BRANCO}" stroke="{BORDA}"/>
      {texto(24, 34, "Índice de produção por atividade · 2022=100", 15, INK, 600)}
      {texto(24, 52, f"{lider[1]} lidera, {numero(lider[3])} pontos acima da média da UF", 12, ACAO)}
      <g transform="translate(24,70)" font-size="11">
        <rect x="0" y="-9" width="10" height="10" fill="{ACAO}"/>{texto(14, 0, "Top 3", 11, INK2)}
        <rect x="70" y="-9" width="10" height="10" fill="{NEUTRO}"/>{texto(84, 0, "Demais", 11, INK2)}
        <line x1="150" y1="-4" x2="168" y2="-4" stroke="{LINHA}" stroke-width="2" stroke-dasharray="4 3"/>{texto(174, 0, f"Média da UF ({numero(media)})", 11, INK2)}
      </g>
      <line x1="{inicio}" y1="84" x2="{inicio}" y2="392" stroke="{NEUTRO}"/>
      {"".join(barras)}
      <line x1="{x_media}" y1="84" x2="{x_media}" y2="392" stroke="{LINHA}" stroke-width="2" stroke-dasharray="4 3"/>
      {"".join(rotulos)}
    </g>"""


def grafico_linha(mensal: list[tuple], selecionado: int) -> str:
    """grafico-02-linha: média mensal da UF, com o mês selecionado na cor de ação e o pico rotulado."""
    valores = [float(v) for _, v in mensal]
    piso, teto = math.floor(min(valores) / 10) * 10, math.ceil(max(valores) / 10) * 10
    esquerda, direita, topo, base = 56, 357, 100, 372
    passo = (direita - esquerda) / (len(valores) - 1)

    def y(valor: float) -> float:
        return round(base - (valor - piso) / (teto - piso) * (base - topo), 1)

    pontos = [(round(esquerda + i * passo, 1), y(v)) for i, v in enumerate(valores)]
    pico = max(range(len(valores)), key=valores.__getitem__)
    grade = "".join(
        f'<line x1="52" y1="{y(v)}" x2="{direita}" y2="{y(v)}" stroke="{GRADE}"/>' + texto(46, y(v) + 4, str(v), 10, INK2, ancora="end")
        for v in range(piso, teto + 1, 10)
    )
    marcadores = "".join(
        f'<circle cx="{px}" cy="{py}" r="3" fill="{BRANCO}" stroke="{LINHA}" stroke-width="1.5"/>'
        for i, (px, py) in enumerate(pontos) if i != selecionado
    )
    sx, sy = pontos[selecionado]
    px, py = pontos[pico]
    meses = "".join(texto(x, 396, MESES[i][:3], 10, INK2, ancora="middle") for i, (x, _) in enumerate(pontos))
    insight = (f"{MESES[selecionado].capitalize()} em {numero(mensal[selecionado][1])}; "
               f"pico em {MESES[pico]} ({numero(mensal[pico][1])})")
    return f"""<g id="visual-1" transform="translate({x_coluna(8):g},240)">
      <rect width="{largura(4):g}" height="412" rx="10" fill="{BRANCO}" stroke="{BORDA}"/>
      {texto(24, 34, "Média das atividades por mês · 2025", 15, INK, 600)}
      {texto(24, 52, insight, 12, ACAO)}
      <g transform="translate(24,70)">
        <circle cx="5" cy="-4" r="4" fill="{ACAO}"/>{texto(14, 0, "Mês selecionado", 11, INK2)}
        <line x1="118" y1="-4" x2="136" y2="-4" stroke="{LINHA}" stroke-width="2"/>{texto(142, 0, "Média da UF", 11, INK2)}
      </g>
      {grade}
      <polyline fill="none" stroke="{LINHA}" stroke-width="2" points="{" ".join(f"{x},{yy}" for x, yy in pontos)}"/>
      {marcadores}
      <circle cx="{sx}" cy="{sy}" r="5" fill="{ACAO}"/>
      {texto(sx, sy - 10, numero(mensal[selecionado][1]), 11, ACAO, 600, "middle")}
      {texto(px, py - 10, numero(mensal[pico][1]), 11, INK2, 600, "middle")}
      {meses}
    </g>"""


def tela_analise(dados: dict[str, list[tuple]], atualizado: str) -> str:
    atividades = dados["atividades"]
    media = atividades[0][4]
    acima = sum(1 for a in atividades if a[3] > 0)
    total = len(atividades)
    lider = atividades[0]
    kpi_1 = f"""{texto(62, 38, lider[1], 15, INK, 600)}
      {texto(62, 58, f"ATIVIDADE LÍDER · CNAE {lider[0]}", 11, INK2, espacamento=1.1)}
      {texto(62, 78, f"Índice {numero(lider[2])} · {com_sinal(lider[3])} sobre a média", 12, INK2)}"""
    kpi_2 = f"""{texto(62, 42, numero(media), 24, INK, 700)}
      {texto(62, 60, "MÉDIA DAS ATIVIDADES · 2022=100", 11, INK2, espacamento=1.1)}
      {texto(62, 78, f"{total} atividades com dado no mês", 12, INK2)}"""
    kpi_3 = f"""{texto(62, 42, f"{acima} de {total}", 24, INK, 700)}
      {texto(62, 60, "ATIVIDADES ACIMA DA MÉDIA DA UF", 11, INK2, espacamento=1.1)}
      <rect x="62" y="70" width="140" height="8" fill="{GRADE}"/><rect x="62" y="70" width="{140 * acima / total:.1f}" height="8" fill="{ACAO}"/>
      {texto(212, 78, f"{round(100 * acima / total)}% das atividades", 12, INK2)}"""
    corpo = f"""{menu("Análise")}
  {cabecalho("Indústria de Transformação — atividades da UF no mês", "jan/2025", atualizado)}
  <g id="filtros" font-size="12">
    <g id="filtro-data"><rect x="998" y="82" width="108" height="26" rx="13" fill="{ACAO}" fill-opacity="0.12"/>{texto(1052, 99, "Jan/2025", 12, ACAO, 600, "middle")}</g>
    <g id="filtro-1"><rect x="1116" y="82" width="140" height="26" rx="6" fill="{BRANCO}" stroke="{BORDA}"/>{texto(1128, 99, "UF: Ceará ▾", 12, INK2)}</g>
  </g>
  <g id="kpis">
    {cartao(1, 0, kpi_1, "ranking")}
    {cartao(2, 4, kpi_2, "functions")}
    {cartao(3, 8, kpi_3, "trend-up")}
  </g>
  <g id="visuais">
    {grafico_barras(atividades, media)}
    {grafico_linha(dados["media_mensal"], 0)}
  </g>
  {rodape(atualizado)}"""
    return tela("Análise — Indústria de Transformação, Ceará, jan/2025", corpo)


def tela_capa(atualizado: str) -> str:
    recorte = ["17 Unidades da Federação com dados na PIM-PF",
               "24 atividades da Indústria de Transformação (CNAE 2.0)",
               "Número-índice da produção física, com base 2022 = 100",
               "Meses de janeiro a dezembro de 2025"]
    perguntas = ["Qual é o índice de cada atividade na UF e no mês?",
                 "Qual é a média das atividades e quem fica acima dela?",
                 "Quais são as 3 atividades com maior índice?",
                 "Como a média da UF evoluiu ao longo de 2025?"]
    lista_recorte = "".join(texto(40, 156 + i * 30, f"• {item}", 14, INK2) for i, item in enumerate(recorte))
    lista_perguntas = "".join(texto(642, 156 + i * 30, f"{i + 1}. {item}", 14, INK) for i, item in enumerate(perguntas))
    corpo = f"""{menu("Capa")}
  {cabecalho("Quais atividades puxam a produção industrial em cada UF?", "jan a dez/2025", atualizado)}
  <g id="visuais">
    <g id="visual-principal" transform="translate({x_coluna(0):g},132)">
      <rect width="{largura(12):g}" height="520" rx="10" fill="{BRANCO}" stroke="{BORDA}"/>
      {texto(40, 64, "RECORTE", 11, INK2, 600, espacamento=1.1)}
      {texto(40, 100, "Indústria de Transformação, 2025", 20, INK, 600)}
      {lista_recorte}
      {texto(642, 64, "O QUE A ANÁLISE RESPONDE", 11, INK2, 600, espacamento=1.1)}
      {texto(642, 100, "Uma UF e um mês por vez", 20, INK, 600)}
      {lista_perguntas}
      <rect x="40" y="290" width="1152" height="1" fill="{BORDA}"/>
      {texto(40, 330, "COMO LER A ANÁLISE", 11, INK2, 600, espacamento=1.1)}
      <rect x="40" y="350" width="12" height="12" fill="{ACAO}"/>{texto(60, 361, "Azul: as 3 atividades de maior índice no mês", 13, INK2)}
      <line x1="420" y1="356" x2="440" y2="356" stroke="{LINHA}" stroke-width="2" stroke-dasharray="4 3"/>{texto(448, 361, "Tracejado: média das atividades da UF", 13, INK2)}
      {texto(780, 361, "(+43,45): diferença do índice para a média", 13, INK2)}
      {texto(40, 391, "Atividades sem dado na UF não aparecem nem contam como zero.", 13, INK2)}
      <rect x="40" y="432" width="220" height="48" rx="8" fill="{ACAO}"/>
      {texto(150, 462, "Abrir a análise →", 15, BRANCO, 600, "middle")}
    </g>
  </g>
  {rodape(atualizado)}"""
    return tela("Capa — Observatório da Indústria, PIM-PF 2025", corpo)


def contraste(frente: str, fundo: str, opacidade_fundo: float = 1.0) -> float:
    """Razão de contraste WCAG. O fundo pode ser uma cor translúcida sobre branco."""
    def canal(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    def rgb(cor: str) -> list[float]:
        return [int(cor[i:i + 2], 16) / 255 for i in (1, 3, 5)]

    def luminancia(cores: list[float]) -> float:
        r, g, b = (canal(c) for c in cores)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    base = [opacidade_fundo * c + (1 - opacidade_fundo) for c in rgb(fundo)]
    claro, escuro = sorted((luminancia(rgb(frente)), luminancia(base)), reverse=True)
    return (claro + 0.05) / (escuro + 0.05)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    dados = consultas()
    atualizado = dados["atualizacao"][0][0].strftime("%d/%m/%Y")
    (PASTA / "tela-01-capa.svg").write_text(tela_capa(atualizado), encoding="utf-8")
    (PASTA / "tela-02-analise.svg").write_text(tela_analise(dados, atualizado), encoding="utf-8")
    pares = [("texto principal", INK, BRANCO, 1), ("texto secundário", INK2, BRANCO, 1),
             ("texto secundário no fundo da página", INK2, FUNDO, 1), ("cor de ação", ACAO, BRANCO, 1),
             ("pílula ativa", ACAO, ACAO, 0.12), ("botão", BRANCO, ACAO, 1)]
    for nome, frente, fundo, opacidade in pares:
        log.info("Contraste %-36s %s sobre %s: %.1f:1", nome, frente, fundo, contraste(frente, fundo, opacidade))
    log.info("Telas geradas em %s", PASTA)


if __name__ == "__main__":
    main()
