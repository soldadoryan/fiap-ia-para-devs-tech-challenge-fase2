"""
Testes da geracao de demanda e da validacao do porte da frota.

A validacao roda uma unica vez, na inicializacao, e e a unica barreira entre um
cenario impossivel e milhares de geracoes presas na penalidade. As mensagens de
erro sao parte do contrato: e por elas que o usuario descobre o que ajustar.
"""

import random

import pytest

from restricoes.entregas import (CRITICO, REGULAR, demanda_total, gerar_entregas,
                                 validar_capacidade)
from restricoes.veiculo import Veiculo


def test_gerar_entregas_cobre_todas_as_cidades(cidades):
    random.seed(7)
    dados = gerar_entregas(cidades, 0.5, 1, 10)

    assert set(dados) == set(cidades)
    for valores in dados.values():
        assert valores["prioridade"] in (CRITICO, REGULAR)
        assert 1 <= valores["demanda"] <= 10


def test_probabilidade_nos_extremos(cidades):
    random.seed(7)
    todos_regulares = gerar_entregas(cidades, 0.0, 1, 1)
    todos_criticos = gerar_entregas(cidades, 1.0, 1, 1)

    assert all(v["prioridade"] == REGULAR for v in todos_regulares.values())
    assert all(v["prioridade"] == CRITICO for v in todos_criticos.values())


def test_demanda_total_ignora_a_base_e_filtra_por_prioridade(cidades, entregas):
    assert demanda_total(cidades, entregas) == 50
    assert demanda_total(cidades, entregas, CRITICO) == 15
    assert demanda_total(cidades, entregas, REGULAR) == 35
    assert demanda_total([], entregas) == 0


def test_frota_vazia_e_recusada(cidades, entregas):
    with pytest.raises(ValueError, match="frota esta vazia"):
        validar_capacidade(cidades, entregas, [])


def test_capacidade_total_insuficiente_e_recusada(cidades, entregas):
    frota = [Veiculo("Mini", capacidade=10, autonomia=999, aceita_criticos=True)]

    with pytest.raises(ValueError, match="Frota subdimensionada"):
        validar_capacidade(cidades, entregas, frota)


def test_capacidade_critica_insuficiente_e_recusada(cidades, entregas):
    """
    A frota comporta a demanda total, mas nao a critica.

    Sem esta checagem o cenario passaria na validacao e so falharia depois, em
    forma de penalidade permanente no fitness.
    """
    frota = [Veiculo("Habilitado", capacidade=10, autonomia=999, aceita_criticos=True),
             Veiculo("Comum", capacidade=90, autonomia=999, aceita_criticos=False)]

    with pytest.raises(ValueError, match="folga para medicamentos criticos"):
        validar_capacidade(cidades, entregas, frota)


def test_folga_confortavel_passa_em_silencio(cidades, entregas, capsys):
    frota = [Veiculo("Grande", capacidade=100, autonomia=999, aceita_criticos=True)]
    validar_capacidade(cidades, entregas, frota)

    assert capsys.readouterr().out == ""


def test_folga_baixa_gera_aviso(cidades, entregas, capsys):
    frota = [Veiculo("Justo", capacidade=55, autonomia=999, aceita_criticos=True)]
    validar_capacidade(cidades, entregas, frota)

    assert "[AVISO]" in capsys.readouterr().out
