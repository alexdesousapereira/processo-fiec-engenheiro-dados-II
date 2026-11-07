"""Regra da Q1: todo o histórico na primeira carga e, depois, os 3 últimos meses publicados."""
from datetime import date

import pytest

from pim_pf import extracao

D1, D2 = date(2026, 11, 5), date(2026, 12, 5)
FONTE = [202501, 202502, 202503, 202504, 202505, 202506]


def controle(*periodos, parciais=(), pendentes=(), data=D1):
    return {
        p: {"data_fonte": data, "completo": p not in parciais, "carregado_em": None if p in pendentes else D1}
        for p in periodos
    }


def test_primeira_carga_escolhe_todos_os_meses():
    assert extracao.periodos_alvo(FONTE, {}, "auto") == FONTE


def test_carga_interrompida_escolhe_os_meses_que_faltam_e_a_janela():
    assert extracao.periodos_alvo(FONTE, controle(202501, 202502), "auto") == [
        202503, 202504, 202505, 202506,
    ]


def test_no_dia_a_dia_escolhe_os_3_ultimos_publicados():
    assert extracao.periodos_alvo(FONTE, controle(*FONTE), "auto") == [202504, 202505, 202506]


def test_mes_parcial_fora_da_janela_continua_sendo_alvo():
    assert extracao.periodos_alvo(FONTE, controle(*FONTE, parciais=[202501]), "auto") == [
        202501, 202504, 202505, 202506,
    ]


def test_mes_novo_entra_mesmo_com_o_controle_em_dia():
    assert 202507 in extracao.periodos_alvo([*FONTE, 202507], controle(*FONTE), "auto")


def test_intervalo_substitui_a_janela():
    assert extracao.periodos_alvo(FONTE, controle(*FONTE), "auto", 202502, 202503) == [202502, 202503]


def test_mes_fora_da_fonte_e_recusado_com_a_lista():
    with pytest.raises(extracao.PeriodosIndisponiveis, match="202507"):
        extracao.periodos_alvo(FONTE, {}, "auto", 202506, 202507)


def test_carga_completa_escolhe_todos():
    assert extracao.periodos_alvo(FONTE, controle(*FONTE), "completa") == FONTE


def test_intervalo_atravessa_a_virada_do_ano():
    assert extracao.meses_do_intervalo(202411, 202502) == [202411, 202412, 202501, 202502]


@pytest.mark.parametrize(
    "inicio, fim, valido",
    [(202301, 202412, True), (202301, 202501, False), (202503, 202501, False)],
)
def test_intervalo_tem_ordem_e_limite_de_24_meses(inicio, fim, valido):
    if valido:
        extracao.validar_intervalo(inicio, fim)
    else:
        with pytest.raises(ValueError):
            extracao.validar_intervalo(inicio, fim)


def test_texto_vira_periodo():
    assert extracao.texto_para_periodo("2025-03") == 202503


def test_data_nova_em_mes_antigo_fora_da_janela_nao_e_novidade():
    # A fonte muda a data de todos os meses de uma vez, e a janela só atualiza os 3 últimos.
    na_fonte = {p: D2 for p in FONTE}
    registro = controle(*FONTE, data=D1)
    for p in (202504, 202505, 202506):
        registro[p]["data_fonte"] = D2
    assert extracao.calcular_novidades(na_fonte, registro) == {
        "ha_novidade": False, "meses_alterados": [], "meses_pendentes": [],
    }


def test_data_nova_na_janela_e_novidade():
    resultado = extracao.calcular_novidades({p: D2 for p in FONTE}, controle(*FONTE, data=D1))
    assert resultado["ha_novidade"] is True
    assert resultado["meses_alterados"] == [202504, 202505, 202506]


def test_mes_pendente_de_carga_e_novidade():
    resultado = extracao.calcular_novidades({p: D1 for p in FONTE}, controle(*FONTE, pendentes=[202501]))
    assert resultado == {"ha_novidade": True, "meses_alterados": [], "meses_pendentes": [202501]}
