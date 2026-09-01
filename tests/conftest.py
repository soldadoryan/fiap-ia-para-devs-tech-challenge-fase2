"""
Fixtures compartilhadas pela suite.

O cenario e propositalmente pequeno e escrito a mao: as entregas NAO sao
sorteadas, porque quase todo teste precisa saber exatamente qual e a demanda de
cada ponto para afirmar sobre carga, penalidade e ocupacao. A geometria tambem e
conhecida - ha um quadrado de lado 100 - para as distancias serem conferiveis na
mao, sem reimplementar o calculo dentro do teste.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from restricoes.entregas import CRITICO, REGULAR
from restricoes.veiculo import Veiculo

BASE = (0, 0)
QUADRADO = [(0, 0), (100, 0), (100, 100), (0, 100)]


@pytest.fixture
def cidades():
    """Seis pontos: o quadrado de lado 100 na origem e dois pontos distantes."""
    return [(0, 0), (100, 0), (100, 100), (0, 100), (300, 0), (300, 100)]


@pytest.fixture
def entregas(cidades):
    """Demanda e prioridade fixas. Total 50, sendo 15 de carga critica."""
    return {
        cidades[0]: {"prioridade": REGULAR, "demanda": 0},
        cidades[1]: {"prioridade": CRITICO, "demanda": 10},
        cidades[2]: {"prioridade": REGULAR, "demanda": 10},
        cidades[3]: {"prioridade": CRITICO, "demanda": 5},
        cidades[4]: {"prioridade": REGULAR, "demanda": 20},
        cidades[5]: {"prioridade": REGULAR, "demanda": 5},
    }


@pytest.fixture
def frota():
    """Dois veiculos folgados; so o primeiro leva carga critica."""
    return [
        Veiculo("Ambulancia", capacidade=40, autonomia=100000, aceita_criticos=True),
        Veiculo("Furgao", capacidade=40, autonomia=100000, aceita_criticos=False),
    ]


@pytest.fixture
def config_limpo(monkeypatch):
    """
    Fixa os pesos da funcao de custo durante o teste.

    Necessario porque os testes de fitness afirmam sobre valores exatos, e
    porque config e um modulo de globais mutaveis em tempo de execucao -
    benchmarks/__main__.py altera CUSTO_FIXO_VEICULO, por exemplo. O monkeypatch
    restaura tudo ao final, entao a ordem dos testes nao importa.
    """
    monkeypatch.setattr(config, "CUSTO_FIXO_VEICULO", 100.0)
    monkeypatch.setattr(config, "PENALIDADE_EXCESSO", 1000.0)
    monkeypatch.setattr(config, "PENALIDADE_AUTONOMIA", 5.0)
    monkeypatch.setattr(config, "PESO_EQUILIBRIO", 0.0)
    monkeypatch.setattr(config, "METROS_POR_PIXEL", 1.0)
    monkeypatch.setattr(config, "VELOCIDADE_MEDIA_KMH", 60.0)
    return config
