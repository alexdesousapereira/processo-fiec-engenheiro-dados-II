"""Gera o projeto do painel (PBIP): modelo semântico em TMDL e relatório em PBIR, seguindo o mockup.

Referência visual: mockup/tela-01-capa.svg e mockup/tela-02-analise.svg (feature 002).
Uso, a partir da raiz do repositório:
    docker run --rm -v "$(pwd):/repo" -w /repo python:3.12.13-slim-bookworm python powerbi/ferramentas/gerar_pbip.py

Recria os arquivos gerados e preserva o que o Power BI Desktop grava por conta própria: o tema do Observatório,
os arquivos .platform (identificação do item) e o diagramLayout.json. As versões de formato são as que o
Desktop gravou ao salvar o projeto, para que abrir e salvar de novo não reescreva os arquivos sem necessidade.
"""
import json
import shutil
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
POWERBI = RAIZ / "powerbi"
SM = POWERBI / "Observatorio.SemanticModel"
REL = POWERBI / "Observatorio.Report"
DEF = REL / "definition"
REG = REL / "StaticResources" / "RegisteredResources"
BASE = REL / "StaticResources" / "SharedResources" / "BaseThemes"

ESQ = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
VC = f"{ESQ}/visualContainer/2.14.0/schema.json"
VERSOES = {"visual": "2.14.0", "report": "3.4.0", "page": "2.3.1"}
NOME_TEMA = "tema_powerbi_fiec_observatorio.json"
LOGO = "logo_fiec.png"
TEMA_BASE = "CY24SU10"

# Tokens do mockup (mockup/observatorio-mockup-racional.md).
ACAO, INK, INK2, NEUTRO, LINHA, BORDA, FUNDO, BRANCO = (
    "#0E4194", "#33394C", "#5C6470", "#C9CDD4", "#7C8595", "#E6E8EC", "#F5F7FB", "#FFFFFF")
# O painel lê só a tabela analítica e as dimensões; as regras do painel (top 3, líder, cores) são medidas DAX.
FATO = "fato_producao_fisica_industrial_2025"
MED = "Medidas"
COLUNA = (1232 - 11 * 20) / 12  # grade de 12 colunas, margem 24, gutter 20


def x_coluna(coluna: int) -> float:
    return round(24 + coluna * (COLUNA + 20), 2)


def largura(colunas: int) -> float:
    return round(colunas * COLUNA + (colunas - 1) * 20, 2)


def escrever(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def escrever_json(caminho: Path, dados: dict) -> None:
    escrever(caminho, json.dumps(dados, indent=2, ensure_ascii=False) + "\n")


# ---------- Modelo semântico ----------

def consulta_m(origem: str, colunas: list[str], filtro: str | None = None,
               adicionais: list[tuple[str, str]] | None = None) -> str:
    """O recorte fica na consulta, para os filtros do painel só listarem UFs, 2025 e atividades.

    `adicionais` cria colunas de texto calculadas na própria consulta, como o rótulo do eixo do mockup.
    """
    passos = [
        "Fonte = PostgreSQL.Database(Servidor & \":\" & Porta, Banco),",
        f"Tabela = Fonte{{[Schema=\"warehouse\",Item=\"{origem}\"]}}[Data],",
    ]
    anterior = "Tabela"
    if filtro:
        passos.append(f"Filtrada = Table.SelectRows(Tabela, each {filtro}),")
        anterior = "Filtrada"
    calculadas = dict(adicionais or [])
    lista = ", ".join(f'"{c}"' for c in colunas if c not in calculadas)
    passos.append(f"Colunas = Table.SelectColumns({anterior}, {{{lista}}})")
    final = "Colunas"
    for i, (nome, expressao) in enumerate(calculadas.items(), start=1):
        passos[-1] += ","
        passos.append(f'Calculada{i} = Table.AddColumn({final}, "{nome}", each {expressao}, type text)')
        final = f"Calculada{i}"
    corpo = "\n".join(f"\t\t\t\t    {p}" for p in passos)
    return f"\t\t\t\tlet\n{corpo}\n\t\t\t\tin\n\t\t\t\t    {final}"


def coluna(nome: str, tipo: str, formato: str | None = None, ordenar: str | None = None) -> str:
    linhas = [f"\tcolumn {nome}", f"\t\tdataType: {tipo}"]
    if formato:
        linhas.append(f"\t\tformatString: {formato}")
    linhas.append("\t\tsummarizeBy: none")
    linhas.append(f"\t\tsourceColumn: {nome}")
    if ordenar:
        linhas.append(f"\t\tsortByColumn: {ordenar}")
    return "\n".join(linhas) + "\n"


def tabela(nome: str, colunas: list[tuple], filtro: str | None = None, medidas: str = "",
           adicionais: list[tuple[str, str]] | None = None, origem: str | None = None) -> str:
    partes = [f"table {nome}\n"]
    if medidas:
        partes.append(medidas)
    for c in colunas:
        partes.append(coluna(*c))
    nomes = [c[0] for c in colunas]
    consulta = consulta_m(origem or nome, nomes, filtro, adicionais)
    partes.append(f"\tpartition {nome} = m\n\t\tmode: import\n\t\tsource =\n{consulta}\n")
    return "\n".join(partes)


COLUNAS_FATO = [
    ("territorio_codigo", "int64", "0"), ("periodo", "int64", "0"), ("categoria_codigo", "int64", "0"),
    ("indice_producao", "double", "#,0.00"), ("media_atividades_uf_mes", "double", "#,0.00"),
    ("diferenca_para_media", "double", "#,0.00"),
]

# Todas as medidas ficam na tabela Medidas. Índice, média e diferença vêm prontos da tabela analítica, para o
# painel mostrar os mesmos números da consulta SQL; o painel só calcula as regras de exibição.
# Os textos usam FORMAT com "pt-BR": vírgula decimal, como no mockup.
MEDIDAS = f"""\tmeasure 'Índice de produção' = AVERAGE({FATO}[indice_producao])
\t\tformatString: #,0.00

\tmeasure 'Média das atividades' = AVERAGE({FATO}[media_atividades_uf_mes])
\t\tformatString: #,0.00

\tmeasure 'Atividades com dado' = DISTINCTCOUNT({FATO}[categoria_codigo]) + 0
\t\tformatString: 0

\tmeasure 'Atividades acima da média' = CALCULATE(DISTINCTCOUNT({FATO}[categoria_codigo]), {FATO}[diferenca_para_media] > 0) + 0
\t\tformatString: 0

\tmeasure 'Acima da média' = FORMAT([Atividades acima da média], "0") & " de " & FORMAT([Atividades com dado], "0")

\tmeasure 'Detalhe acima da média' = FORMAT(DIVIDE([Atividades acima da média], [Atividades com dado]), "0%", "pt-BR") & " das atividades"

\tmeasure 'Detalhe da média' = FORMAT([Atividades com dado], "0") & " atividades com dado no mês"

\tmeasure 'Posição no ranking' =
\t\t\tVAR indice = [Índice de produção]
\t\t\tVAR codigo = SELECTEDVALUE(dim_categorias[categoria_codigo])
\t\t\tVAR ranking = FILTER(ADDCOLUMNS(ALLSELECTED(dim_categorias), "@indice", [Índice de produção]), NOT ISBLANK([@indice]))
\t\t\tRETURN
\t\t\t\tIF(NOT ISBLANK(indice) && NOT ISBLANK(codigo),
\t\t\t\t\t1 + COUNTROWS(FILTER(ranking, [@indice] > indice || ([@indice] = indice && dim_categorias[categoria_codigo] < codigo))))
\t\tformatString: 0

\tmeasure 'Cor do ranking' =
\t\t\tVAR posicao = [Posição no ranking]
\t\t\tRETURN IF(NOT ISBLANK(posicao) && posicao <= 3, "{ACAO}", "{NEUTRO}")

\tmeasure 'Código do líder' =
\t\t\tVAR ranking = FILTER(ADDCOLUMNS(VALUES(dim_categorias[categoria_codigo]), "@indice", [Índice de produção]), NOT ISBLANK([@indice]))
\t\t\tRETURN MAXX(TOPN(1, ranking, [@indice], DESC, dim_categorias[categoria_codigo], ASC), dim_categorias[categoria_codigo])
\t\tformatString: 0
\t\tisHidden

\tmeasure 'Atividade líder' =
\t\t\tVAR codigo = [Código do líder]
\t\t\tRETURN IF(ISBLANK(codigo), "Selecione uma UF e um mês",
\t\t\t\tLOOKUPVALUE(dim_categorias[categoria_nome], dim_categorias[categoria_codigo], codigo))

\tmeasure 'Índice do líder' =
\t\t\tVAR codigo = [Código do líder]
\t\t\tRETURN CALCULATE([Índice de produção], dim_categorias[categoria_codigo] = codigo)
\t\tformatString: #,0.00

\tmeasure 'Diferença do líder' =
\t\t\tVAR codigo = [Código do líder]
\t\t\tRETURN CALCULATE(AVERAGE({FATO}[diferenca_para_media]), dim_categorias[categoria_codigo] = codigo)
\t\tformatString: +#,0.00;-#,0.00;0.00

\tmeasure 'Detalhe do líder' =
\t\t\t"Índice " & FORMAT([Índice do líder], "#,0.00", "pt-BR") & " · "
\t\t\t\t& FORMAT([Diferença do líder], "+#,0.00;-#,0.00", "pt-BR") & " sobre a média"

\tmeasure 'Insight do líder' = [Atividade líder] & " lidera, " & FORMAT([Diferença do líder], "#,0.00", "pt-BR") & " pontos acima da média da UF"

\tmeasure 'Carimbo de data' =
\t\t\t"Dados: " & LEFT(SELECTEDVALUE(dim_calendario[mes_nome], "vários meses"), 3) & "/2025 · atualizado em "
\t\t\t\t& FORMAT(MAX(dim_territorio[data_carga]), "dd/mm/yyyy")

\tmeasure 'Legenda da média' = "Média da UF (" & FORMAT([Média das atividades], "#,0.00", "pt-BR") & ")"

\tmeasure 'Carimbo do período' = "Dados: jan a dez/2025 · atualizado em " & FORMAT(MAX(dim_territorio[data_carga]), "dd/mm/yyyy")

\tmeasure 'Insight da linha' =
\t\t\tVAR mes = SELECTEDVALUE(dim_calendario[mes_nome])
\t\t\tVAR meses = ADDCOLUMNS(ALL(dim_calendario[periodo], dim_calendario[mes_nome]), "@media", CALCULATE([Média das atividades]))
\t\t\tVAR pico = TOPN(1, meses, [@media], DESC)
\t\t\tRETURN
\t\t\t\tUPPER(LEFT(mes, 1)) & MID(mes, 2, 20) & " em " & FORMAT([Média das atividades], "#,0.00", "pt-BR")
\t\t\t\t\t& "; pico em " & MAXX(pico, dim_calendario[mes_nome]) & " (" & FORMAT(MAXX(pico, [@media]), "#,0.00", "pt-BR") & ")"

"""


def tabela_medidas() -> str:
    """Tabela só para guardar as medidas: uma coluna oculta e nenhuma linha. O Desktop a mostra com o ícone de medidas."""
    return (f"table {MED}\n\n{MEDIDAS}"
            "\tcolumn Coluna\n\t\tdataType: string\n\t\tisHidden\n\t\tsummarizeBy: none\n\t\tsourceColumn: Coluna\n\n"
            f"\tpartition {MED} = m\n\t\tmode: import\n\t\tsource = #table(type table [Coluna = text], {{}})\n")


def gerar_modelo() -> None:
    escrever_json(SM / "definition.pbism", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2",
        "settings": {},
    })
    escrever(SM / "definition" / "database.tmdl", "database\n\tcompatibilityLevel: 1606\n")
    tabelas = ["dim_calendario", "dim_categorias", "dim_territorio", FATO, MED]
    refs = "\n".join(f"ref table {t}" for t in tabelas)
    escrever(SM / "definition" / "model.tmdl", f"""model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-US
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation __PBI_TimeIntelligenceEnabled = 0

annotation PBI_ProTooling = ["DevMode"]

{refs}
""")
    parametros = [("Servidor", "localhost"), ("Porta", "5432"), ("Banco", "pim")]
    escrever(SM / "definition" / "expressions.tmdl", "\n".join(
        f'expression {nome} = "{valor}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n'
        f"\tannotation PBI_ResultType = Text\n"
        for nome, valor in parametros
    ))

    t = SM / "definition" / "tables"
    escrever(t / "dim_calendario.tmdl", tabela("dim_calendario", [
        ("periodo", "int64", "0"), ("ano", "int64", "0"), ("mes", "int64", "0"),
        ("mes_nome", "string", None, "mes"),
        # Eixo do gráfico mensal (jan, fev...), já calculado no dbt.
        ("mes_curto", "string", None, "mes"),
    ], "[ano] = 2025"))
    escrever(t / "dim_categorias.tmdl", tabela("dim_categorias", [
        ("categoria_codigo", "int64", "0"), ("categoria_cnae", "string"), ("categoria_nome", "string"),
        ("categoria_rotulo", "string"),
    ], "[eh_atividade_transformacao] = true",
        # Rótulo do eixo das barras no mockup: "3.13 Fabricação de produtos têxteis".
        adicionais=[("categoria_rotulo", '[categoria_cnae] & " " & [categoria_nome]')]))
    # data_carga alimenta o carimbo "atualizado em" das duas telas.
    escrever(t / "dim_territorio.tmdl", tabela("dim_territorio", [
        ("territorio_codigo", "int64", "0"), ("territorio_nome", "string"), ("data_carga", "dateTime", "dd/mm/yyyy"),
    ], '[nivel] = "N3"'))
    escrever(t / f"{FATO}.tmdl", tabela(FATO, COLUNAS_FATO))
    escrever(t / f"{MED}.tmdl", tabela_medidas())

    ligacoes = [
        (FATO, de, para) for de, para in (
            ("territorio_codigo", "dim_territorio.territorio_codigo"),
            ("periodo", "dim_calendario.periodo"),
            ("categoria_codigo", "dim_categorias.categoria_codigo"),
        )
    ]
    # Sem crossFilteringBehavior: o padrão é o filtro em uma só direção, da dimensão para a tabela analítica.
    escrever(SM / "definition" / "relationships.tmdl", "\n".join(
        f"relationship {uuid.uuid5(uuid.NAMESPACE_DNS, f'{v}.{de}')}\n"
        f"\tfromColumn: {v}.{de}\n\ttoColumn: {para}\n"
        for v, de, para in ligacoes
    ))


# ---------- Relatório ----------

def lit(valor: str) -> dict:
    return {"expr": {"Literal": {"Value": valor}}}


def texto(valor: str) -> dict:
    return lit("'" + valor.replace("'", "''") + "'")


def cor(hexa: str) -> dict:
    return {"solid": {"color": texto(hexa)}}


def col(entidade: str, nome: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Entity": entidade}}, "Property": nome}}


def med(entidade: str, nome: str) -> dict:
    return {"Measure": {"Expression": {"SourceRef": {"Entity": entidade}}, "Property": nome}}


def projecao(campo: dict) -> dict:
    alvo = campo.get("Column") or campo["Measure"]
    entidade, nome = alvo["Expression"]["SourceRef"]["Entity"], alvo["Property"]
    return {"field": campo, "queryRef": f"{entidade}.{nome}", "nativeQueryRef": nome, "active": True}


def moldura(alt: str, titulo: str | None = None, subtitulo: dict | None = None, fundo: bool = True) -> dict:
    """Título descritivo e subtítulo de insight, como no mockup (rótulo fixo ou medida)."""
    m = {"general": [{"properties": {"altText": texto(alt)}}]}
    if titulo:
        m["title"] = [{"properties": {
            "show": lit("true"), "text": texto(titulo), "fontColor": cor(INK), "fontSize": lit("11D"), "bold": lit("true"),
        }}]
    else:
        m["title"] = [{"properties": {"show": lit("false")}}]
    if subtitulo:
        m["subTitle"] = [{"properties": {"show": lit("true"), "text": subtitulo, "fontColor": cor(ACAO), "fontSize": lit("9D")}}]
    if fundo:
        m["border"] = [{"properties": {"show": lit("true"), "color": cor(BORDA), "radius": lit("10D")}}]
    else:
        m["background"] = [{"properties": {"show": lit("false")}}]
        m["border"] = [{"properties": {"show": lit("false")}}]
    return m


def estado_padrao(propriedades: dict) -> list[dict]:
    """Botões guardam a formatação por estado (padrão, focalizado, pressionado).

    O `show` não depende de estado e fica numa entrada sem seletor; o resto vai no estado padrão.
    Com o `show` dentro do seletor, o Desktop o ignora e desenha o botão vazio, só com o contorno.
    """
    estado = {k: v for k, v in propriedades.items() if k != "show"}
    entradas = [{"properties": {"show": propriedades["show"]}}] if "show" in propriedades else []
    if estado:
        entradas.append({"properties": estado, "selector": {"id": "default"}})
    return entradas


def container(pagina: str, nome: str, tipo: str, x: float, y: float, l: float, a: float, ordem: int,
              consulta: dict | None = None, objetos: dict | None = None, moldura_visual: dict | None = None,
              ordenar: tuple | None = None) -> None:
    visual = {"visualType": tipo}
    if consulta:
        visual["query"] = {"queryState": {b: {"projections": [projecao(c) for c in cs]} for b, cs in consulta.items()}}
        if ordenar:
            visual["query"]["sortDefinition"] = {"sort": [{"field": ordenar[0], "direction": ordenar[1]}], "isDefaultSort": False}
    if objetos:
        visual["objects"] = objetos
    if moldura_visual:
        visual["visualContainerObjects"] = moldura_visual
    visual["drillFilterOtherVisuals"] = True
    escrever_json(DEF / "pages" / pagina / "visuals" / nome / "visual.json", {
        "$schema": VC,
        "name": nome,
        "position": {"x": x, "y": y, "z": ordem * 1000, "height": a, "width": l, "tabOrder": ordem * 1000},
        "visual": visual,
    })


def caixa_texto(pagina: str, nome: str, x: float, y: float, l: float, a: float, ordem: int,
                paragrafos: list[list[tuple[str, int, str, bool]]], alt: str, fundo: str | None = None) -> None:
    """Texto fixo. Cada parágrafo é uma lista de trechos (texto, tamanho em pt, cor, negrito)."""
    corpo = [{"textRuns": [{"value": t, "textStyle": {"fontSize": f"{tam}pt", "color": c, "fontWeight": "bold" if n else "normal"}}
                           for t, tam, c, n in p]} for p in paragrafos]
    m = moldura(alt, fundo=False)
    if fundo:
        m["background"] = [{"properties": {"show": lit("true"), "color": cor(fundo), "transparency": lit("0D")}}]
    container(pagina, nome, "textbox", x, y, l, a, ordem, objetos={"general": [{"properties": {"paragraphs": corpo}}]}, moldura_visual=m)


def cartao_texto(pagina: str, nome: str, x: float, y: float, l: float, a: float, ordem: int, medida: dict, alt: str,
                 tamanho: int = 10, cor_texto: str = INK2) -> None:
    """Valor de uma medida de texto, sem moldura: carimbos de data."""
    container(pagina, nome, "card", x, y, l, a, ordem, consulta={"Values": [medida]},
              objetos={"labels": [{"properties": {"fontSize": lit(f"{tamanho}D"), "color": cor(cor_texto)}}],
                       "categoryLabels": [{"properties": {"show": lit("false")}}]},
              moldura_visual=moldura(alt, fundo=False))


def barra_marca(pagina: str, ativa: str) -> None:
    """Barra branca do topo, com o logo da FIEC, a marca e as abas Capa e Análise (no mockup, a camada menu)."""
    caixa_texto(pagina, f"{pagina}_barra", 0, 0, 1280, 60, 1, [[("", 10, INK, False)]], "Barra superior", fundo=BRANCO)
    container(pagina, f"{pagina}_logo", "image", 24, 13, 119, 34, 2,
              objetos={
                  "general": [{"properties": {"imageUrl": {"expr": {"ResourcePackageItem": {
                      "PackageName": "RegisteredResources", "PackageType": 1, "ItemName": LOGO}}}}}],
                  "imageScaling": [{"properties": {"imageScalingType": texto("Fit")}}],
              },
              moldura_visual=moldura("Logo da FIEC, Federação das Indústrias do Estado do Ceará", fundo=False))
    caixa_texto(pagina, f"{pagina}_marca", 168, 12, 260, 36, 3,
                [[("Observatório da Indústria", 12, INK, True)]], "Observatório da Indústria")
    for i, (nome, destino) in enumerate((("Capa", "capa"), ("Análise", "analise"))):
        ativo = nome == ativa
        objetos = {
            "icon": estado_padrao({"show": lit("false")}),
            "text": estado_padrao({"show": lit("true"), "text": texto(nome), "fontColor": cor(ACAO if ativo else INK2),
                                   "fontSize": lit("10D"), "bold": lit("true" if ativo else "false")}),
            "fill": estado_padrao({"show": lit("false")}),
            "outline": estado_padrao({"show": lit("false")}),
        }
        m = {"general": [{"properties": {"altText": texto(f"Aba {nome}")}}]}
        if not ativo:
            m["visualLink"] = [{"properties": {"show": lit("true"), "type": texto("PageNavigation"),
                                               "navigationSection": texto(destino), "tooltip": texto(f"Abrir a tela {nome}")}}]
        x = 430 + i * 76
        container(pagina, f"{pagina}_aba_{destino}", "actionButton", x, 14, 72, 32, 4 + i, objetos=objetos, moldura_visual=m)
        if ativo:
            # Sublinhado azul da aba ativa, como no mockup.
            sublinhado = 34 if nome == "Capa" else 54
            caixa_texto(pagina, f"{pagina}_aba_sublinhado", x + (72 - sublinhado) / 2, 44, sublinhado, 3, 6,
                        [[("", 1, ACAO, False)]], f"Indica que a tela {nome} está aberta", fundo=ACAO)


def rodape(pagina: str) -> None:
    caixa_texto(pagina, f"{pagina}_rodape", 16, 668, 1248, 40, 90, [[
        ("Fonte: IBGE, Pesquisa Industrial Mensal – Produção Física (PIM-PF), tabela 8888 do SIDRA. "
         "Atividades sem dado na UF não aparecem nem contam como zero.", 8, INK2, False)]], "Fonte dos dados")


def filtro_inicial(entidade: str, coluna_nome: str, valor: str) -> dict:
    """O painel abre no caso conferido à mão: Ceará, janeiro de 2025."""
    return {"filter": {
        "Version": 2,
        "From": [{"Name": "d", "Entity": entidade, "Type": 0}],
        "Where": [{"Condition": {"In": {
            "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": coluna_nome}}],
            "Values": [[{"Literal": {"Value": f"'{valor}'"}}]],
        }}}],
    }}


def filtro_lista(nome: str, posicao: tuple[float, float, float, float], ordem: int, entidade: str, coluna_nome: str,
                 inicial: str, rotulo: str) -> None:
    """Filtro de lista suspensa. `posicao` é (x, y, largura, altura)."""
    x, y, l, a = posicao
    m = moldura(f"Filtro de {rotulo.lower()}. Escolha uma opção por vez.", rotulo)
    container("analise", nome, "slicer", x, y, l, a, ordem, consulta={"Values": [col(entidade, coluna_nome)]},
              objetos={
                  "data": [{"properties": {"mode": texto("Dropdown")}}],
                  "selection": [{"properties": {"strictSingleSelect": lit("true")}}],
                  "header": [{"properties": {"show": lit("false")}}],
                  "general": [{"properties": {"filter": filtro_inicial(entidade, coluna_nome, inicial)}}],
              }, moldura_visual=m)


def kpi(nome: str, coluna_inicial: int, ordem: int, valor: dict, titulo: str, detalhe: dict, alt: str, tamanho: int) -> None:
    """Cartão da faixa de KPIs: título descritivo, valor e uma linha de contexto.

    O cartão nativo não exibiu o subtítulo no Desktop; a linha de contexto vem de um segundo cartão,
    sem moldura, sobreposto à parte de baixo do primeiro.
    """
    x = x_coluna(coluna_inicial)
    container("analise", nome, "card", x, 132, largura(4), 88, ordem,
              consulta={"Values": [valor]},
              objetos={"labels": [{"properties": {"fontSize": lit(f"{tamanho}D"), "color": cor(INK)}}],
                       "categoryLabels": [{"properties": {"show": lit("false")}}],
                       "wordWrap": [{"properties": {"show": lit("true")}}]},
              moldura_visual=moldura(alt, titulo))
    cartao_texto("analise", f"{nome}_detalhe", x + 8, 132 + 62, largura(4) - 16, 24, ordem + 50, detalhe,
                 f"Contexto: {titulo.lower()}", tamanho=9)


def pagina_json(nome: str, exibicao: str, extras: dict | None = None) -> None:
    escrever_json(DEF / "pages" / nome / "page.json", {
        "$schema": f"{ESQ}/page/2.0.0/schema.json", "displayOption": "FitToPage", "height": 720, "width": 1280,
        "name": nome, "displayName": exibicao,
        "objects": {"background": [{"properties": {"color": cor(FUNDO), "transparency": lit("0D")}}]},
        **(extras or {}),
    })


def gerar_analise() -> None:
    # O filtro de mês não age sobre a linha, que mostra sempre os 12 meses de 2025.
    pagina_json("analise", "Análise", {"visualInteractions": [
        {"source": "filtro_mes", "target": "linha_media", "type": "NoFilter"}]})
    barra_marca("analise", "Análise")
    caixa_texto("analise", "analise_titulo", 16, 62, 900, 44, 10,
                [[("Indústria de Transformação — atividades da UF no mês", 16, INK, True)]], "Título da tela de análise")
    cartao_texto("analise", "analise_carimbo", 16, 100, 420, 26, 11, med(MED, "Carimbo de data"),
                 "Mês de referência dos dados e data de atualização")
    # Posições ajustadas no Desktop: na altura do mockup, o título do filtro cortava a lista.
    filtro_lista("filtro_mes", (915.71, 60, 191.43, 65.71), 12, "dim_calendario", "mes_nome", "janeiro", "Mês de 2025")
    filtro_lista("filtro_uf", (1118.57, 61.43, 138.57, 64.29), 13, "dim_territorio", "territorio_nome", "Ceará", "UF")

    kpi("cartao_lider", 0, 20, med(MED, "Atividade líder"), "Atividade líder", med(MED, "Detalhe do líder"),
        "Atividade de maior índice na UF e no mês, com o índice e a diferença para a média", 12)
    kpi("cartao_media", 4, 21, med(MED, "Média das atividades"), "Média das atividades · 2022=100", med(MED, "Detalhe da média"),
        "Média dos índices das atividades da UF no mês", 20)
    kpi("cartao_acima", 8, 22, med(MED, "Acima da média"), "Atividades acima da média da UF", med(MED, "Detalhe acima da média"),
        "Quantas atividades estão acima da média da UF no mês", 20)

    container("analise", "barras_indice", "clusteredBarChart", x_coluna(0), 240, largura(8), 412, 30,
              consulta={"Category": [col("dim_categorias", "categoria_rotulo")], "Y": [med(MED, "Índice de produção")]},
              ordenar=(med(MED, "Índice de produção"), "Descending"),
              objetos={
                  "labels": [{"properties": {"show": lit("true"), "color": cor(INK2)}}],
                  "legend": [{"properties": {"show": lit("false")}}],
                  # A cor por medida vale para todas as barras só com o seletor dataViewWildcard.
                  "dataPoint": [{"properties": {"fill": {"solid": {"color": {"expr": med(MED, "Cor do ranking")}}}},
                                 "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}],
                  "categoryAxis": [{"properties": {"showAxisTitle": lit("false"), "labelColor": cor(INK2)}}],
                  # Sem eixo de valores: os rótulos já mostram o índice, como no mockup.
                  "valueAxis": [{"properties": {"show": lit("false"), "showAxisTitle": lit("false"), "start": lit("0D")}}],
                  # Linha constante na média: no mockup, o tracejado "Média da UF".
                  "y1AxisReferenceLine": [{"properties": {
                      "show": lit("true"), "displayName": texto("Média da UF"), "value": {"expr": med(MED, "Média das atividades")},
                      "lineColor": cor(LINHA), "style": texto("dashed"), "transparency": lit("0D"),
                      # Sem rótulo na linha: ele cobria a primeira barra. O valor vai na legenda, como no mockup.
                      "dataLabelShow": lit("false"),
                  }, "selector": {"id": "1"}}],
              },
              moldura_visual={
                  **moldura("Barras com o índice de cada atividade, o top 3 em destaque e a linha da média da UF",
                            "Índice de produção por atividade · 2022=100", {"expr": med(MED, "Insight do líder")}),
                  # Espaço entre o subtítulo e as barras, onde fica a legenda.
                  "spacing": [{"properties": {"customizeSpacing": lit("true"), "spaceBelowTitleArea": lit("26D")}}],
              })
    # Legenda do mockup: "■ Top 3  ■ Demais  - - - Média da UF (101,58)". A parte fixa é texto; o valor vem de medida.
    caixa_texto("analise", "barras_legenda", x_coluna(0) + 16, 286, 180, 24, 32, [[
        ("■", 9, ACAO, False), (" Top 3    ", 9, INK2, False),
        ("■", 9, NEUTRO, False), (" Demais    ", 9, INK2, False),
        ("- - -", 9, LINHA, True),
    ]], "Legenda: azul para o top 3, cinza para as demais, tracejado para a média da UF")
    cartao_texto("analise", "barras_legenda_media", x_coluna(0) + 190, 286, 130, 24, 33, med(MED, "Legenda da média"),
                 "Valor da média da UF no mês", tamanho=9)
    # A linha mostra os 12 meses porque o filtro de mês não age sobre ela (visualInteractions em page.json).
    container("analise", "linha_media", "lineChart", x_coluna(8), 240, largura(4), 412, 31,
              consulta={"Category": [col("dim_calendario", "mes_curto")], "Y": [med(MED, "Média das atividades")]},
              objetos={
                  "labels": [{"properties": {"show": lit("false")}}],
                  "legend": [{"properties": {"show": lit("false")}}],
                  "lineStyles": [{"properties": {"strokeWidth": lit("2D"), "showMarker": lit("true")}}],
                  "dataPoint": [{"properties": {"fill": cor(LINHA)}, "selector": {"metadata": f"{MED}.Média das atividades"}}],
                  "categoryAxis": [{"properties": {"showAxisTitle": lit("false"), "labelColor": cor(INK2)}}],
                  "valueAxis": [{"properties": {"showAxisTitle": lit("false"), "labelColor": cor(INK2)}}],
              },
              moldura_visual={
                  **moldura("Linha com a média dos índices das atividades da UF em cada mês de 2025",
                            "Média das atividades por mês · 2025"),
                  # Espaço sob o título, onde fica o cartão do insight.
                  "spacing": [{"properties": {"customizeSpacing": lit("true"), "spaceBelowTitleArea": lit("26D")}}],
              })
    # O insight cita o mês escolhido. Como subtítulo da linha, ele não veria o filtro de mês desligado;
    # num cartão à parte, sobre o lugar do subtítulo, ele recebe o filtro.
    cartao_texto("analise", "linha_insight", x_coluna(8) + 8, 262, largura(4) - 16, 24, 34, med(MED, "Insight da linha"),
                 "Insight: média do mês escolhido e mês de pico em 2025", tamanho=9, cor_texto=ACAO)
    rodape("analise")


def gerar_capa() -> None:
    pagina_json("capa", "Capa")
    barra_marca("capa", "Capa")
    caixa_texto("capa", "capa_titulo", 16, 62, 1000, 44, 10,
                [[("Quais atividades puxam a produção industrial em cada UF?", 16, INK, True)]], "Título do painel")
    cartao_texto("capa", "capa_carimbo", 16, 100, 420, 26, 11, med(MED, "Carimbo do período"),
                 "Período dos dados e data de atualização")
    caixa_texto("capa", "capa_painel", x_coluna(0), 132, largura(12), 520, 12, [[("", 10, INK, False)]],
                "Área de conteúdo da capa", fundo=BRANCO)
    caixa_texto("capa", "capa_recorte", 56, 168, 560, 200, 13, [
        [("RECORTE", 8, INK2, True)],
        [("Indústria de Transformação, 2025", 15, INK, True)],
        [("• 17 Unidades da Federação com dados na PIM-PF", 10, INK2, False)],
        [("• 24 atividades da Indústria de Transformação (CNAE 2.0)", 10, INK2, False)],
        [("• Número-índice da produção física, com base 2022 = 100", 10, INK2, False)],
        [("• Meses de janeiro a dezembro de 2025", 10, INK2, False)],
    ], "Recorte da análise")
    caixa_texto("capa", "capa_perguntas", 658, 168, 580, 200, 14, [
        [("O QUE A ANÁLISE RESPONDE", 8, INK2, True)],
        [("Uma UF e um mês por vez", 15, INK, True)],
        [("1. Qual é o índice de cada atividade na UF e no mês?", 10, INK, False)],
        [("2. Qual é a média das atividades e quem fica acima dela?", 10, INK, False)],
        [("3. Quais são as 3 atividades com maior índice?", 10, INK, False)],
        [("4. Como a média da UF evoluiu ao longo de 2025?", 10, INK, False)],
    ], "Perguntas que a análise responde")
    caixa_texto("capa", "capa_como_ler", 56, 440, 1180, 100, 15, [
        [("COMO LER A ANÁLISE", 8, INK2, True)],
        [("Azul escuro: as 3 atividades de maior índice no mês.   Tracejado: média das atividades da UF.   "
          "Números entre parênteses: diferença do índice para a média.", 10, INK2, False)],
        [("Atividades sem dado na UF não aparecem nem contam como zero.", 10, INK2, False)],
    ], "Como ler a análise")
    container("capa", "capa_botao", "actionButton", 64, 564, 220, 48, 16,
              objetos={
                  "icon": estado_padrao({"show": lit("false")}),
                  "text": estado_padrao({"show": lit("true"), "text": texto("Abrir a análise →"), "fontColor": cor(BRANCO),
                                         "fontSize": lit("11D"), "bold": lit("true")}),
                  "fill": estado_padrao({"show": lit("true"), "fillColor": cor(ACAO), "transparency": lit("0D")}),
                  "outline": estado_padrao({"show": lit("false")}),
              },
              moldura_visual={
                  "general": [{"properties": {"altText": texto("Botão que abre a tela de análise")}}],
                  "visualLink": [{"properties": {"show": lit("true"), "type": texto("PageNavigation"),
                                                 "navigationSection": texto("analise"), "tooltip": texto("Abrir a tela de análise")}}],
              })
    rodape("capa")


def gerar_relatorio() -> None:
    escrever_json(REL / "definition.pbir", {
        "$schema": f"{ESQ}Properties/2.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byPath": {"path": "../Observatorio.SemanticModel"}},
    })
    escrever_json(DEF / "version.json", {"$schema": f"{ESQ}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    escrever_json(DEF / "report.json", {
        "$schema": f"{ESQ}/report/3.3.0/schema.json",
        "themeCollection": {
            "baseTheme": {"name": TEMA_BASE, "reportVersionAtImport": VERSOES, "type": "SharedResources"},
            "customTheme": {"name": NOME_TEMA, "reportVersionAtImport": VERSOES, "type": "RegisteredResources"},
        },
        "resourcePackages": [
            {"name": "SharedResources", "type": "SharedResources", "items": [
                {"name": TEMA_BASE, "path": f"BaseThemes/{TEMA_BASE}.json", "type": "BaseTheme"},
            ]},
            {"name": "RegisteredResources", "type": "RegisteredResources", "items": [
                {"name": NOME_TEMA, "path": NOME_TEMA, "type": "CustomTheme"},
                {"name": LOGO, "path": LOGO, "type": "Image"},
            ]},
        ],
        "settings": {"useEnhancedTooltips": False},
    })
    tema = json.loads(TEMA_ORIGINAL.decode("utf-8"))
    ensure_parent(REG / NOME_TEMA).write_bytes(TEMA_ORIGINAL)
    # Mesmo arquivo do mockup (mockup/assets/logo-fiec.png), em PNG: o Desktop descartou imagens SVG.
    (REG / LOGO).write_bytes((RAIZ / "mockup" / "assets" / "logo-fiec.png").read_bytes())
    escrever_json(BASE / f"{TEMA_BASE}.json", {
        "name": TEMA_BASE,
        "dataColors": tema["dataColors"],
        "foreground": tema["foreground"],
        "background": tema["background"],
        "tableAccent": tema["tableAccent"],
    })
    escrever_json(DEF / "pages" / "pages.json", {
        "$schema": f"{ESQ}/pagesMetadata/1.1.0/schema.json",
        "pageOrder": ["capa", "analise"],
        # Abre na análise, como ficou salvo no Desktop.
        "activePageName": "analise",
    })
    gerar_capa()
    gerar_analise()
    escrever_json(POWERBI / "Observatorio.pbip", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [{"report": {"path": "Observatorio.Report"}}],
        "settings": {"enableAutoRecovery": True},
    })


def ensure_parent(caminho: Path) -> Path:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    return caminho


# Entradas que não são geradas: lidas antes de recriar as pastas e regravadas como estavam.
TEMA_ORIGINAL = (REG / NOME_TEMA).read_bytes()
PRESERVADOS = {p: p.read_bytes() for p in (REL / ".platform", SM / ".platform", SM / "diagramLayout.json") if p.exists()}
for gerado in (SM, REL):
    if gerado.exists():
        shutil.rmtree(gerado)
gerar_modelo()
gerar_relatorio()
for caminho, conteudo in PRESERVADOS.items():
    ensure_parent(caminho).write_bytes(conteudo)
print("arquivos:", sum(1 for p in POWERBI.rglob("*") if p.is_file() and "ferramentas" not in p.parts))
