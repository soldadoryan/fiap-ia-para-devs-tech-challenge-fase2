"""
Decodificador: traduz a permutacao do GA nas rotas concretas da frota.

E aqui que o VRP acontece. O cromossomo continua sendo uma permutacao simples,
e todo o reparo (capacidade, prioridade, habilitacao) e feito na LEITURA dele -
por isso nenhum filho nasce invalido e os operadores geneticos ficam intactos.
"""

from typing import Dict, List, Sequence

from algoritmo_genetico.avaliacao import calculate_distance
from restricoes.entregas import CRITICO, Cidade
from restricoes.veiculo import Veiculo


def _distribuir(fila: List[Cidade], entregas: Dict[Cidade, dict],
                veiculos: Sequence[Veiculo], indices: List[int],
                carteiras: List[List[Cidade]], cargas: List[int]) -> None:
    """
    Distribui uma fila de entregas entre os veiculos de `indices` (next-fit).

    Enche o veiculo atual ate a proxima entrega nao caber na capacidade DELE; so
    entao passa pro proximo da lista. Como o objetivo e atender a demanda com o
    MENOR numero de veiculos, preencher antes de abrir mais um e exatamente o
    comportamento desejado - o veiculo seguinte so entra quando o anterior nao
    da conta.

    Blocos contiguos: entregas vizinhas no cromossomo continuam vizinhas na mesma
    rota, que e o que preserva a geometria aprendida pelo GA. Chegando no ultimo
    veiculo, tudo que sobrar vai pra ele mesmo assim - nenhuma entrega fica sem
    atendimento, e o excesso e cobrado depois pela penalidade no fitness.
    """
    if not fila or not indices:
        return

    posicao = 0
    for city in fila:
        demanda = entregas[city]["demanda"]
        veiculo_atual = indices[posicao]

        while (posicao < len(indices) - 1
               and cargas[veiculo_atual] > 0
               and cargas[veiculo_atual] + demanda > veiculos[veiculo_atual].capacidade):
            posicao += 1
            veiculo_atual = indices[posicao]

        carteiras[veiculo_atual].append(city)
        cargas[veiculo_atual] += demanda


def decodificar_rotas(individual: List[Cidade], entregas: Dict[Cidade, dict],
                      veiculos: Sequence[Veiculo]) -> List[List[Cidade]]:
    """
    Traduz a permutacao em uma rota por veiculo da frota.

    1. Base: a primeira cidade do cromossomo e o hospital. Todos os veiculos
       partem dela e voltam pra ela. Como ela faz parte da permutacao, o GA
       tambem escolhe qual ponto e a melhor base.
    2. A fila de entregas e separada em criticos e regulares, preservando a ordem
       que o cromossomo propos (e ai que mora a otimizacao geometrica do GA).
    3. Os criticos sao distribuidos primeiro, e SO entre os veiculos habilitados
       (aceita_criticos) - restricao rigida de quem pode levar o que.
    4. Os regulares sao distribuidos depois, entre todos os veiculos, ocupando a
       capacidade que sobrou.
    5. Cada rota fica [base] + criticos + regulares: dentro de cada veiculo os
       criticos saem sempre antes dos regulares, que e a restricao de prioridade.

    Retorna uma lista alinhada com `veiculos`. Um veiculo sem entrega fica com a
    rota [base] apenas.
    """
    if not individual:
        return []

    base = individual[0]
    fila = individual[1:]

    criticos = [c for c in fila if entregas[c]["prioridade"] == CRITICO]
    regulares = [c for c in fila if entregas[c]["prioridade"] != CRITICO]

    carteiras_criticas: List[List[Cidade]] = [[] for _ in veiculos]
    carteiras_regulares: List[List[Cidade]] = [[] for _ in veiculos]
    cargas = [0 for _ in veiculos]

    habilitados = [i for i, v in enumerate(veiculos) if v.aceita_criticos]
    if not habilitados:
        habilitados = list(range(len(veiculos)))

    _distribuir(criticos, entregas, veiculos, habilitados, carteiras_criticas, cargas)
    _distribuir(regulares, entregas, veiculos, list(range(len(veiculos))),
                carteiras_regulares, cargas)

    return [[base] + carteiras_criticas[i] + carteiras_regulares[i]
            for i in range(len(veiculos))]


def carga_da_rota(rota: List[Cidade], entregas: Dict[Cidade, dict]) -> int:
    """Carga transportada numa rota (ignora a base, que e o primeiro ponto)."""
    return sum(entregas[c]["demanda"] for c in rota[1:])


def distancia_da_rota(rota: List[Cidade]) -> float:
    """
    Distancia de uma rota fechada, em metros: base -> entregas -> base.

    Rota com so a base (veiculo que nao saiu da garagem) custa zero.
    """
    n = len(rota)
    if n < 2:
        return 0.0
    return sum(calculate_distance(rota[i], rota[(i + 1) % n]) for i in range(n))


if __name__ == "__main__":
    import random

    import config
    from restricoes.entregas import (REGULAR, demanda_total, gerar_entregas,
                                  validar_capacidade)
    from restricoes.fitness import calcular_fitness_logistico, resumo_da_frota

    frota = [Veiculo.da_config(d) for d in config.FROTA]
    cidades = [(random.randint(0, 800), random.randint(0, 800))
               for _ in range(config.N_CITIES)]
    dados = gerar_entregas(cidades, config.PROB_CRITICO,
                           config.DEMANDA_MIN, config.DEMANDA_MAX)
    validar_capacidade(cidades, dados, frota)

    individuo = random.sample(cidades, len(cidades))
    rotas = decodificar_rotas(individuo, dados, frota)
    base = individuo[0]

    assert len(rotas) == len(frota), f"{len(rotas)} rotas para {len(frota)} veiculos"
    assert all(rota[0] == base for rota in rotas), "alguma rota nao parte da base"

    for veiculo, rota in zip(frota, rotas):
        carga = carga_da_rota(rota, dados)
        assert carga <= veiculo.capacidade, \
            f"{veiculo.nome} estourou: {carga} > {veiculo.capacidade}"

    atendidas = [c for rota in rotas for c in rota[1:]]
    assert sorted(atendidas) == sorted(c for c in individuo if c != base)
    assert len(atendidas) == len(set(atendidas)), "cidade atendida mais de uma vez"

    for veiculo, rota in zip(frota, rotas):
        if not veiculo.aceita_criticos:
            assert all(dados[c]["prioridade"] != CRITICO for c in rota[1:]), \
                f"{veiculo.nome} recebeu carga critica sem habilitacao"

    for veiculo, rota in zip(frota, rotas):
        prioridades = [dados[c]["prioridade"] for c in rota[1:]]
        if REGULAR in prioridades:
            primeiro_regular = prioridades.index(REGULAR)
            assert CRITICO not in prioridades[primeiro_regular:], \
                f"{veiculo.nome} atende critico depois de regular"

    print(f"OK - demanda total {demanda_total(cidades, dados)} "
          f"(critica {demanda_total(cidades, dados, CRITICO)})")
    print(resumo_da_frota(rotas, dados, frota))
    print(f"custo = {calcular_fitness_logistico(individuo, dados, frota):.2f}")
