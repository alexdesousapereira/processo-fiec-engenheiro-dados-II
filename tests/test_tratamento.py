import pandas as pd
import pytest
from conftest import LOCALIDADES, METADADOS, linha_valor

from pim_pf import carga, tratamento


def quadro(*linhas: dict) -> pd.DataFrame:
    return pd.DataFrame(list(linhas))


def variaveis(lista: list[dict] | None = None) -> pd.DataFrame:
    return pd.DataFrame(METADADOS["variaveis"] if lista is None else lista)


def test_valor_numerico_fica_sem_simbolo():
    df = tratamento.tratar(quadro(linha_valor()))
    assert df.loc[0, "valor"] == 145.03
    assert df["simbolo_origem"].isna().all()


@pytest.mark.parametrize("simbolo", ["-", "...", "..", "X"])
def test_simbolo_vira_nulo_nunca_zero_e_fica_preservado(simbolo):
    df = tratamento.tratar(quadro(linha_valor(valor=simbolo)))
    assert df["valor"].isna().all()
    assert df.loc[0, "simbolo_origem"] == simbolo


def test_simbolo_desconhecido_interrompe_a_carga():
    with pytest.raises(tratamento.DadosInvalidos, match="desconhecidos"):
        tratamento.tratar(quadro(linha_valor(valor="abc")))


def test_linha_sem_valor_e_sem_simbolo_interrompe_a_carga():
    with pytest.raises(tratamento.DadosInvalidos, match="sem valor"):
        tratamento.tratar(quadro(linha_valor(valor=None)))


def test_indice_negativo_interrompe_a_carga():
    with pytest.raises(tratamento.DadosInvalidos, match="negativos"):
        tratamento.tratar(quadro(linha_valor(valor="-1.5")))


def test_variacao_negativa_e_valida():
    df = tratamento.tratar(quadro(linha_valor(valor="-1.5", variavel="11602")))
    assert df.loc[0, "valor"] == -1.5


def test_duplicidade_mantem_uma_linha_por_chave():
    df = tratamento.tratar(quadro(linha_valor(), linha_valor()))
    assert len(df) == 1


def test_producao_tem_tipos_explicitos():
    df = tratamento.tratar(quadro(linha_valor()))
    for coluna in tratamento.CHAVE:
        assert df[coluna].dtype == "int64"
    assert df["valor"].dtype == "float64"


def test_tabela_de_producao_tem_as_colunas_da_stage():
    df = tratamento.tratar(quadro(linha_valor()))
    df["execucao_id"], df["path_origem"], df["data_carga"] = "exec", "arquivo", pd.Timestamp("2026-11-07")
    assert list(tratamento.tabela_producao(df).columns) == [
        "territorio_codigo", "periodo", "variavel_codigo", "categoria_codigo",
        "valor", "simbolo_origem", "execucao_id", "path_origem", "data_carga",
    ]


def test_variaveis_vem_dos_metadados_com_unidade():
    df = tratamento.tratar_variaveis(variaveis())
    assert list(df.columns) == ["variavel_codigo", "variavel_nome", "unidade"]
    assert df["variavel_codigo"].tolist() == [12606, 11602]
    assert df["unidade"].tolist() == ["Número-índice", "%"]


def test_variavel_sem_unidade_interrompe_a_carga():
    with pytest.raises(tratamento.DadosInvalidos, match="unidade"):
        tratamento.tratar_variaveis(variaveis([{"id": 1, "nome": "x", "unidade": None}]))


@pytest.mark.parametrize(
    "codigo, cnae, nome, eh_atividade",
    [
        (129320, "3.13", "Fabricação de produtos têxteis", True),
        (56689, "3.20", "Fabricação de produtos químicos", True),  # código fora da sequência
        (129316, "3", "Indústrias de transformação", False),  # agregado, não é atividade
    ],
)
def test_atividade_e_identificada_pelo_padrao_e_nao_pelo_codigo(codigo, cnae, nome, eh_atividade):
    entrada = pd.DataFrame(METADADOS["classificacoes"][0]["categorias"])
    df = tratamento.tratar_categorias(entrada).set_index("categoria_codigo")
    assert df.loc[codigo, "categoria_cnae"] == cnae
    assert df.loc[codigo, "categoria_nome"] == nome
    assert bool(df.loc[codigo, "eh_atividade_transformacao"]) is eh_atividade


def test_territorio_tem_codigo_inteiro_e_nivel():
    entrada = pd.DataFrame([
        {"id": "1", "nome": "Brasil", "nivel": "N1"},
        {"id": "23", "nome": "Ceará", "nivel": "N3"},
    ])
    df = tratamento.tratar_territorio(entrada)
    assert list(df.columns) == ["territorio_codigo", "territorio_nome", "nivel"]
    assert df["territorio_codigo"].tolist() == [1, 23]
    assert df["nivel"].tolist() == ["N1", "N3"]


def test_conversao_do_json_das_localidades_junta_os_niveis():
    df = carga.quadro_territorio(LOCALIDADES)
    assert df["id"].tolist() == ["1", "2", "23"]
    assert df["nivel"].tolist() == ["N1", "N2", "N3"]
