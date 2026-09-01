"""
Testes do decodificador - o coracao do projeto.

E aqui que a permutacao do GA vira rotas concretas, e e aqui que as restricoes
rigidas do VRP sao garantidas. Se estes testes passam, nenhum individuo que o GA
produzir pode gerar uma solucao que viole prioridade ou habilitacao.
"""

import random

import pytest

from restricoes.entregas import CRITICO, REGULAR, demanda_total
from restricoes.roteirizacao import (carga_da_rota, decodificar_rotas,
                                     distancia_da_rota)
from restricoes.veiculo import Veiculo

SEMENTES = range(30)


def _permutacoes(cidades):
    """Varias permutacoes reprodutiveis das mesmas cidades."""
    for semente in SEMENTES:
        random.seed(semente)
        yield random.sample(cidades, len(cidades))


def test_toda_rota_parte_da_base(cidades, entregas, frota):
    for individuo in _permutacoes(cidades):
        rotas = decodificar_rotas(individuo, entregas, frota)
        assert all(rota[0] == individuo[0] for rota in rotas)


def test_toda_entrega_atendida_exatamente_uma_vez(cidades, entregas, frota):
    for individuo in _permutacoes(cidades):
        rotas = decodificar_rotas(individuo, entregas, frota)
        atendidas = [c for rota in rotas for c in rota[1:]]

        assert len(atendidas) == len(set(atendidas)), "cidade atendida duas vezes"
        assert sorted(atendidas) == sorted(c for c in individuo if c != individuo[0])


def test_criticos_sempre_antes_dos_regulares(cidades, entregas, frota):
    """Restricao rigida de prioridade, garantida pela ordem da concatenacao."""
    for individuo in _permutacoes(cidades):
        for rota in decodificar_rotas(individuo, entregas, frota):
            prioridades = [entregas[c]["prioridade"] for c in rota[1:]]
            if REGULAR in prioridades:
                primeiro_regular = prioridades.index(REGULAR)
                assert CRITICO not in prioridades[primeiro_regular:]


def test_veiculo_sem_habilitacao_nunca_leva_carga_critica(cidades, entregas, frota):
    """Restricao rigida de habilitacao: so aceita_criticos recebe critico."""
    for individuo in _permutacoes(cidades):
        rotas = decodificar_rotas(individuo, entregas, frota)
        for veiculo, rota in zip(frota, rotas):
            if not veiculo.aceita_criticos:
                assert all(entregas[c]["prioridade"] != CRITICO for c in rota[1:])


def test_critico_nao_transborda_para_veiculo_sem_habilitacao(cidades, entregas):
    """
    O caso que realmente exercita o filtro de habilitacao.

    O veiculo habilitado e pequeno demais para toda a carga critica, e o outro
    tem capacidade de sobra. Se o decodificador distribuisse os criticos entre
    todos, o excedente cairia no veiculo sem habilitacao - e o correto e ele
    estourar no habilitado, porque quem nao pode levar, nao leva.
    """
    frota = [Veiculo("Habilitado", capacidade=10, autonomia=99999,
                     aceita_criticos=True),
             Veiculo("Comum", capacidade=100, autonomia=99999,
                     aceita_criticos=False)]

    for individuo in _permutacoes(cidades):
        rotas = decodificar_rotas(individuo, entregas, frota)
        criticos_no_comum = [c for c in rotas[1][1:]
                             if entregas[c]["prioridade"] == CRITICO]

        assert criticos_no_comum == [], "carga critica foi parar em veiculo comum"

        criticos_no_habilitado = sum(entregas[c]["demanda"] for c in rotas[0][1:]
                                     if entregas[c]["prioridade"] == CRITICO)
        assert criticos_no_habilitado == demanda_total(individuo, entregas, CRITICO)


def test_com_folga_nenhum_veiculo_estoura_a_capacidade(cidades, entregas, frota):
    for individuo in _permutacoes(cidades):
        rotas = decodificar_rotas(individuo, entregas, frota)
        for veiculo, rota in zip(frota, rotas):
            assert carga_da_rota(rota, entregas) <= veiculo.capacidade


def test_individuo_vazio_devolve_lista_vazia(entregas, frota):
    assert decodificar_rotas([], entregas, frota) == []


def test_sempre_devolve_uma_rota_por_veiculo(cidades, entregas, frota):
    """Alinhamento posicional com a frota: vrp.py e o fitness usam zip()."""
    frota_grande = frota + [Veiculo("Reserva", capacidade=99, autonomia=99999)]
    rotas = decodificar_rotas(cidades, entregas, frota_grande)

    assert len(rotas) == len(frota_grande)


def test_veiculo_ocioso_fica_so_com_a_base(cidades, entregas):
    """Um veiculo folgado o bastante deixa os outros na garagem."""
    frota = [Veiculo("Grandao", capacidade=999, autonomia=99999, aceita_criticos=True),
             Veiculo("Ocioso", capacidade=999, autonomia=99999, aceita_criticos=True)]
    rotas = decodificar_rotas(cidades, entregas, frota)

    assert rotas[1] == [cidades[0]]
    assert carga_da_rota(rotas[1], entregas) == 0
    assert distancia_da_rota(rotas[1]) == 0.0


def test_frota_sem_nenhum_habilitado_recebe_os_criticos_mesmo_assim(cidades, entregas):
    """
    Fallback do decodificador: sem veiculo habilitado, todos ficam elegiveis.

    E preferivel entregar sem habilitacao a deixar carga critica sem
    atendimento - e o cenario e barrado antes disso por validar_capacidade.
    """
    frota = [Veiculo("Comum", capacidade=999, autonomia=99999, aceita_criticos=False)]
    rotas = decodificar_rotas(cidades, entregas, frota)
    atendidas = rotas[0][1:]

    assert sorted(atendidas) == sorted(cidades[1:])


def test_capacidade_apertada_nao_descarta_entrega(cidades, entregas):
    """
    Next-fit: chegando ao ultimo veiculo, o excesso vai pra ele mesmo assim.

    O fitness depende deste contrato - ele cobra o excesso como penalidade, o que
    so faz sentido se nenhuma entrega tiver sumido no caminho.
    """
    frota = [Veiculo("Pequeno 1", capacidade=1, autonomia=10, aceita_criticos=True),
             Veiculo("Pequeno 2", capacidade=1, autonomia=10, aceita_criticos=True)]
    rotas = decodificar_rotas(cidades, entregas, frota)
    atendidas = [c for rota in rotas for c in rota[1:]]

    assert sorted(atendidas) == sorted(cidades[1:])
    assert sum(carga_da_rota(r, entregas) for r in rotas) == 50


def test_carga_da_rota_ignora_a_base(cidades, entregas):
    rota = [cidades[0], cidades[1], cidades[2]]

    assert carga_da_rota(rota, entregas) == 20
    assert carga_da_rota([cidades[0]], entregas) == 0


def test_distancia_de_rota_fechada(cidades):
    """Quadrado de lado 100: 4 lados, porque a rota volta para a base."""
    quadrado = [(0, 0), (100, 0), (100, 100), (0, 100)]

    assert distancia_da_rota(quadrado) == pytest.approx(400.0)
    assert distancia_da_rota([(0, 0), (30, 40)]) == pytest.approx(100.0)


def test_distancia_de_veiculo_que_nao_saiu_da_garagem():
    assert distancia_da_rota([(0, 0)]) == 0.0
    assert distancia_da_rota([]) == 0.0


def test_decodificador_e_deterministico(cidades, entregas, frota):
    """
    O GA so converge porque o mesmo cromossomo sempre gera as mesmas rotas.

    Sem isso o fitness de um individuo mudaria entre geracoes e a busca perderia
    o chao.
    """
    individuo = list(reversed(cidades))

    assert (decodificar_rotas(individuo, entregas, frota)
            == decodificar_rotas(individuo, entregas, frota))
