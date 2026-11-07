import json

import pytest
import requests
from conftest import LOCALIDADES, METADADOS, RespostaFalsa, SessaoFalsa

from pim_pf import fonte


def test_localidades_juntam_os_tres_niveis():
    sessao = SessaoFalsa({f"/localidades/{n}": itens for n, itens in LOCALIDADES.items()})
    conteudo = json.loads(fonte.buscar_localidades(sessao))
    assert {n: len(itens) for n, itens in conteudo.items()} == {"N1": 1, "N2": 1, "N3": 1}


def test_localidades_preservam_os_bytes_de_cada_resposta():
    original = '[ {"id": "1",  "nome": "Brasil"} ]'.encode()
    sessao = SessaoFalsa({"/localidades/": original})
    conteudo = fonte.buscar_localidades(sessao)
    assert conteudo.count(original) == 3
    assert list(json.loads(conteudo)) == ["N1", "N2", "N3"]


def test_toda_chamada_tem_tempo_limite():
    sessao = SessaoFalsa({"/metadados": METADADOS, "/periodos": [], "/values": []})
    fonte.buscar_metadados(sessao)
    fonte.buscar_periodos(sessao)
    fonte.buscar_valores(sessao, 202501)
    assert [t for _, t in sessao.chamadas] == [fonte.TEMPO_LIMITE] * 3


def test_toda_chamada_verifica_o_status():
    class SessaoComErro(SessaoFalsa):
        def get(self, url, timeout=None):
            return RespostaFalsa([], status=500)

    with pytest.raises(fonte.FonteIndisponivel):
        fonte.buscar_valores(SessaoComErro(), 202501)


def test_tentativas_esgotadas_viram_fonte_indisponivel():
    sessao = SessaoFalsa(erro=requests.exceptions.RetryError("muitas tentativas"))
    with pytest.raises(fonte.FonteIndisponivel):
        fonte.buscar_periodos(sessao)


@pytest.mark.parametrize("sem", ["variaveis", "classificacoes"])
def test_metadados_incompletos_sao_estrutura_alterada(sem):
    corpo = {k: v for k, v in METADADOS.items() if k != sem}
    with pytest.raises(fonte.EstruturaAlterada):
        fonte.buscar_metadados(SessaoFalsa({"/metadados": corpo}))


def test_periodos_em_formato_inesperado_sao_estrutura_alterada():
    with pytest.raises(fonte.EstruturaAlterada):
        fonte.buscar_periodos(SessaoFalsa({"/periodos": [{"sem_id": 1}]}))


def test_localidades_vazias_sao_estrutura_alterada():
    with pytest.raises(fonte.EstruturaAlterada):
        fonte.buscar_localidades(SessaoFalsa({"/localidades/": []}))
