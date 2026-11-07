"""Tratamento com pandas (T1 a T6). São funções puras, testadas sem banco e sem rede."""
import logging

import pandas as pd

log = logging.getLogger(__name__)

# ADR 0004: "-" é atividade sem dado na UF e "..." é dado indisponível. Viram nulo, nunca zero.
SIMBOLOS_CONHECIDOS = {"-", "..", "...", "X"}
VARIAVEIS_DE_INDICE = {12606, 12607}
# Padrão da atividade de transformação: 3.NN. Faixa de códigos falharia, pois a 3.20 usa o 56689.
PADRAO_ATIVIDADE = r"^3\.\d{2}$"

NOMES = {  # T3: nomes padronizados
    "V": "valor_origem",
    "D1C": "territorio_codigo",
    "D2C": "variavel_codigo",
    "D3C": "periodo",
    "D4C": "categoria_codigo",
}
CHAVE = ["territorio_codigo", "periodo", "variavel_codigo", "categoria_codigo"]
COLUNAS_PRODUCAO = [*CHAVE, "valor", "simbolo_origem", "execucao_id", "path_origem", "data_carga"]


class DadosInvalidos(ValueError):
    """Dado que a regra não sabe tratar. Interrompe a carga antes de chegar à Stage."""


def padronizar(linhas: pd.DataFrame) -> pd.DataFrame:
    """T3 e T4: renomeia, define tipos e separa o valor do símbolo."""
    df = linhas.rename(columns=NOMES)[list(NOMES.values())].copy()
    for coluna in CHAVE:
        df[coluna] = df[coluna].astype("int64")

    # T5: errors="coerce" faz todo texto virar nulo; o que era texto fica em simbolo_origem,
    # e `validar` recusa o que não estiver na lista de símbolos conhecidos.
    df["valor"] = pd.to_numeric(df["valor_origem"], errors="coerce").astype("float64")
    df["simbolo_origem"] = df["valor_origem"].where(df["valor"].isna())
    return df


def validar(df: pd.DataFrame) -> None:
    """T2 e T5: recusa o que a regra não conhece, em vez de transformar em nulo sem aviso."""
    simbolos = set(df["simbolo_origem"].dropna()) - SIMBOLOS_CONHECIDOS
    if simbolos:
        raise DadosInvalidos(f"Símbolos desconhecidos: {sorted(simbolos)}")

    vazias = df[df["valor"].isna() & df["simbolo_origem"].isna()]
    if not vazias.empty:
        raise DadosInvalidos(f"Linhas sem valor e sem símbolo: {vazias[CHAVE].head().to_dict('records')}")

    indices = df[df["variavel_codigo"].isin(VARIAVEIS_DE_INDICE) & df["valor"].notna()]
    negativos = indices[indices["valor"] < 0]
    if not negativos.empty:
        raise DadosInvalidos(f"Índices negativos: {negativos[CHAVE + ['valor']].head().to_dict('records')}")


def remover_duplicidades(df: pd.DataFrame) -> pd.DataFrame:
    """T6: mantém uma linha por chave e registra quantas foram removidas."""
    sem_duplicidade = df.drop_duplicates(subset=CHAVE, keep="last")
    removidas = len(df) - len(sem_duplicidade)
    if removidas:
        log.warning("Duplicidades removidas: %d", removidas)
    return sem_duplicidade


def tratar(linhas: pd.DataFrame) -> pd.DataFrame:
    df = remover_duplicidades(padronizar(linhas))
    validar(df)
    return df


def tabela_producao(df: pd.DataFrame) -> pd.DataFrame:
    """Seleciona as colunas de `stage.producao_fisica`."""
    return df[COLUNAS_PRODUCAO]


def tratar_variaveis(variaveis: pd.DataFrame) -> pd.DataFrame:
    df = variaveis.rename(columns={"id": "variavel_codigo", "nome": "variavel_nome"})[
        ["variavel_codigo", "variavel_nome", "unidade"]
    ].astype({"variavel_codigo": "int64"})
    sem_unidade = df[df["unidade"].fillna("") == ""]
    if not sem_unidade.empty:
        raise DadosInvalidos(f"Variáveis sem unidade: {sem_unidade['variavel_codigo'].tolist()}")
    return df


def tratar_categorias(categorias: pd.DataFrame) -> pd.DataFrame:
    df = categorias.rename(columns={"id": "categoria_codigo", "nome": "rotulo"})[
        ["categoria_codigo", "rotulo"]
    ].astype({"categoria_codigo": "int64"})
    # "3.10 Fabricação de..." vira CNAE "3.10" e nome "Fabricação de..."
    partes = df["rotulo"].str.split(" ", n=1, expand=True)
    df["categoria_cnae"], df["categoria_nome"] = partes[0], partes[1]
    df["eh_atividade_transformacao"] = df["categoria_cnae"].str.match(PADRAO_ATIVIDADE)
    return df[["categoria_codigo", "categoria_cnae", "categoria_nome", "eh_atividade_transformacao"]]


def tratar_territorio(localidades: pd.DataFrame) -> pd.DataFrame:
    return localidades.rename(columns={"id": "territorio_codigo", "nome": "territorio_nome"})[
        ["territorio_codigo", "territorio_nome", "nivel"]
    ].astype({"territorio_codigo": "int64"})
