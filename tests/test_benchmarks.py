"""
Testes da instancia fixa att48 e do dimensionamento da frota do benchmark.

O att48 so serve de referencia se for mesmo reprodutivel e se o tour otimo
carregado corresponder as cidades carregadas. O teste do dimensionamento e a
regressao do erro "Frota subdimensionada" que o modo vrp dava com a frota crua
de config.py.
"""

import random

import pytest

import config
from benchmarks.att48 import ATT48_COORDENADAS, carregar, comprimento_otimo
from benchmarks.__main__ import FOLGA_ALVO, _frota_dimensionada
from restricoes.entregas import CRITICO, demanda_total, gerar_entregas


def test_carregar_devolve_as_48_cidades_na_tela():
    cidades, _ = carregar(1600, 900, margem=10, x_offset=800)

    assert len(cidades) == len(ATT48_COORDENADAS) == 48
    assert all(800 <= x <= 1600 and 0 <= y <= 900 for x, y in cidades)
    assert len(set(cidades)) == 48, "o reescalonamento colidiu duas cidades"


def test_tour_otimo_e_uma_permutacao_das_cidades():
    """
    A cidade de fechamento duplicada do arquivo original e removida no carregar.

    Se ela ficasse, o tour teria 49 pontos e a comparacao com o GA - que trabalha
    com 48 - seria entre coisas diferentes.
    """
    cidades, tour = carregar(1600, 900, x_offset=800)

    assert len(tour) == len(cidades)
    assert sorted(tour) == sorted(cidades)


def test_instancia_e_reprodutivel():
    """O ponto do benchmark: o mesmo mapa em toda execucao."""
    primeira, tour_1 = carregar(1600, 900, x_offset=800)
    segunda, tour_2 = carregar(1600, 900, x_offset=800)

    assert primeira == segunda
    assert comprimento_otimo(tour_1) == comprimento_otimo(tour_2)


def test_comprimento_otimo_e_positivo():
    _, tour = carregar(1600, 900, x_offset=800)

    assert comprimento_otimo(tour) > 0


def test_frota_e_replicada_ate_caber_a_demanda(capsys):
    """
    Regressao: as 48 entregas do att48 nao cabem na FROTA de config.py.

    A frota do cenario principal e dimensionada para N_CITIES pontos. Em vez de
    exigir que o usuario a desbalanceie, o benchmark despacha turnos inteiros.
    """
    random.seed(42)
    cidades, _ = carregar(1600, 900, x_offset=800)
    entregas = gerar_entregas(cidades, config.PROB_CRITICO,
                              config.DEMANDA_MIN, config.DEMANDA_MAX)

    frota = _frota_dimensionada(cidades, entregas)
    capacidade = sum(v.capacidade for v in frota)

    assert capacidade >= demanda_total(cidades, entregas) * FOLGA_ALVO
    assert len(frota) % len(config.FROTA) == 0
    assert "replicada" in capsys.readouterr().out


def test_replicacao_preserva_a_capacidade_para_carga_critica():
    random.seed(42)
    cidades, _ = carregar(1600, 900, x_offset=800)
    entregas = gerar_entregas(cidades, config.PROB_CRITICO,
                              config.DEMANDA_MIN, config.DEMANDA_MAX)

    frota = _frota_dimensionada(cidades, entregas)
    habilitada = sum(v.capacidade for v in frota if v.aceita_criticos)

    assert habilitada >= demanda_total(cidades, entregas, CRITICO) * FOLGA_ALVO


def test_frota_folgada_nao_e_replicada(cidades, entregas, capsys):
    """Cabendo de primeira, a frota sai igual a de config.py - sem sufixo."""
    frota = _frota_dimensionada(cidades, entregas)

    assert len(frota) == len(config.FROTA)
    assert [v.nome for v in frota] == [v["nome"] for v in config.FROTA]
    assert capsys.readouterr().out == ""
