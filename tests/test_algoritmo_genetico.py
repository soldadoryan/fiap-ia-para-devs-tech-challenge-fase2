"""
Testes dos operadores geneticos puros.

A propriedade que atravessa quase todos: o individuo e uma PERMUTACAO. Nenhum
operador pode repetir ou perder uma cidade - e disso que vem a garantia de que
nenhum filho nasce invalido e de que o decodificador nunca recebe lixo.
"""

import random

import pytest

from algoritmo_genetico.avaliacao import calculate_distance, sort_population
from algoritmo_genetico.cruzamento import order_crossover
from algoritmo_genetico.mutacao import mutate
from algoritmo_genetico.populacao import generate_random_population
from algoritmo_genetico.selecao import selecao_por_roleta


def _e_permutacao(individuo, cidades):
    return sorted(individuo) == sorted(cidades)


def test_distancia_euclidiana():
    assert calculate_distance((0, 0), (3, 4)) == pytest.approx(5.0)
    assert calculate_distance((10, 10), (10, 10)) == 0.0


def test_populacao_inicial_so_tem_permutacoes(cidades):
    random.seed(1)
    populacao = generate_random_population(cidades, 25)

    assert len(populacao) == 25
    assert all(_e_permutacao(ind, cidades) for ind in populacao)


def test_order_crossover_preserva_a_permutacao(cidades):
    """
    A razao de existir do OX.

    Um crossover de corte simples produziria filhos com cidade repetida e outra
    faltando; o OX herda uma fatia de um pai e completa na ordem do outro.
    """
    for semente in range(50):
        random.seed(semente)
        pai1 = random.sample(cidades, len(cidades))
        pai2 = random.sample(cidades, len(cidades))

        filho = order_crossover(pai1, pai2)

        assert len(filho) == len(cidades)
        assert _e_permutacao(filho, cidades), f"semente {semente} gerou filho invalido"


def test_order_crossover_realmente_recombina_os_dois_pais(cidades):
    """
    O filho tem que herdar do pai 2 tambem.

    O codigo base do desafio chamava order_crossover(parent1, parent1), e nesse
    regime o operador devolve sempre o proprio pai: nao ha recombinacao nenhuma e
    a busca vira mutacao pura. Este teste tranca essa porta.
    """
    diferentes = 0
    for semente in range(50):
        random.seed(semente)
        pai1 = random.sample(cidades, len(cidades))
        pai2 = random.sample(cidades, len(cidades))

        if order_crossover(pai1, pai2) != pai1:
            diferentes += 1

    assert diferentes > 0, "o filho nunca difere do pai 1: nao houve recombinacao"


def test_mutacao_com_probabilidade_zero_nao_altera(cidades):
    assert mutate(cidades, 0.0) == cidades


def test_mutacao_preserva_a_permutacao_e_nao_toca_no_original(cidades):
    for semente in range(50):
        random.seed(semente)
        original = random.sample(cidades, len(cidades))
        copia = list(original)

        mutado = mutate(original, 1.0)

        assert _e_permutacao(mutado, cidades)
        assert original == copia, "o deepcopy falhou: o individuo original mudou"


def test_mutacao_em_individuo_minusculo_nao_quebra():
    assert mutate([(0, 0)], 1.0) == [(0, 0)]
    assert mutate([], 1.0) == []


def test_sort_population_ordena_do_melhor_para_o_pior():
    populacao = [["c"], ["a"], ["b"]]
    fitness = [30.0, 10.0, 20.0]

    ordenada, ordenado = sort_population(populacao, fitness)

    assert list(ordenado) == [10.0, 20.0, 30.0]
    assert list(ordenada) == [["a"], ["b"], ["c"]], "o pareamento se perdeu"


def test_roleta_devolve_dois_individuos_da_populacao(cidades):
    random.seed(3)
    populacao = generate_random_population(cidades, 10)
    fitness = [float(i + 1) for i in range(10)]

    pai1, pai2 = selecao_por_roleta(populacao, fitness)

    assert pai1 in populacao
    assert pai2 in populacao


def test_roleta_favorece_o_individuo_de_menor_custo(cidades):
    """
    O 1/fitness da roleta: aqui fitness e custo, entao o barato tem a fatia maior.

    Sem a inversao a selecao empurraria a populacao para as piores rotas.
    """
    random.seed(11)
    barato, caro = [(0, 0)], [(1, 1)]
    populacao = [barato, caro]
    fitness = [1.0, 1000.0]

    escolhas = [selecao_por_roleta(populacao, fitness)[0] for _ in range(200)]

    assert escolhas.count(barato) > escolhas.count(caro)
