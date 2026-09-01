"""
Runner do benchmark att48. Sem janela, sem relatorio: so o algoritmo.

    python -m benchmarks            # modo tsp, 500 geracoes
    python -m benchmarks tsp 2000   # compara com o otimo conhecido
    python -m benchmarks vrp 2000   # a frota hospitalar completa no mapa fixo

Dois modos, porque so um deles admite comparacao com o otimo publicado:

- tsp: reduz o problema a um unico veiculo folgado, sem custo de frota, sem
  autonomia e com todas as entregas regulares. Nesse regime o VRP degenera
  exatamente no TSP original do att48, e ai sim faz sentido medir a distancia
  contra o tour otimo conhecido.
- vrp: roda a frota de config.py sobre a mesma instancia fixa, replicando-a em
  turnos quando as 48 entregas nao cabem nela. Nao existe otimo
  publicado para este problema (frota heterogenea, prioridade, capacidade,
  autonomia, custo por veiculo), entao o numero serve para comparar execucoes
  entre si - parametros, operadores, versoes -, nao contra uma referencia.
"""

import random
import sys
import time

import config
from benchmarks.att48 import carregar, comprimento_otimo
from restricoes.entregas import REGULAR
from restricoes.fitness import calcular_fitness_logistico, resumo_da_frota
from restricoes.roteirizacao import decodificar_rotas, distancia_da_rota
from restricoes.veiculo import Veiculo, km
from algoritmo_genetico.avaliacao import sort_population
from algoritmo_genetico.cruzamento import order_crossover
from algoritmo_genetico.mutacao import mutate
from algoritmo_genetico.populacao import generate_random_population
from algoritmo_genetico.selecao import selecao_por_roleta

GERACOES_PADRAO = 500

AVISO_FROTA = ("\n\nO att48 tem 48 pontos de entrega, bem mais que config.N_CITIES, "
               "e nem replicando a frota de config.py a demanda coube. Reduza "
               "DEMANDA_MAX ou aumente a capacidade dos veiculos em config.py.")

FOLGA_ALVO = 1.3
MAX_TURNOS = 20


def _frota_dimensionada(cidades, entregas):
    """
    Replica a frota de config.py ate ela dar conta das 48 entregas do att48.

    A FROTA de config.py e dimensionada para config.N_CITIES pontos; o att48 tem
    bem mais que isso, entao rodar o modo vrp com ela crua sempre estouraria a
    capacidade. Em vez de pedir pro usuario desbalancear a frota do cenario
    principal, o benchmark despacha turnos inteiros da mesma frota - o que
    preserva a proporcao entre os veiculos, a heterogeneidade e a habilitacao
    para carga critica, mudando so a escala.
    """
    from restricoes.entregas import CRITICO, demanda_total

    total = demanda_total(cidades, entregas)
    total_critico = demanda_total(cidades, entregas, CRITICO)

    capacidade = sum(v["capacidade"] for v in config.FROTA)
    capacidade_critica = sum(v["capacidade"] for v in config.FROTA
                             if v["aceita_criticos"])

    turnos = 1
    while turnos < MAX_TURNOS:
        if (turnos * capacidade >= total * FOLGA_ALVO
                and turnos * capacidade_critica >= total_critico * FOLGA_ALVO):
            break
        if not capacidade_critica and total_critico:
            break
        turnos += 1

    frota = []
    for turno in range(1, turnos + 1):
        for dados in config.FROTA:
            veiculo = Veiculo.da_config(dados)
            if turnos > 1:
                veiculo.nome = f"{veiculo.nome} {turno}"
            frota.append(veiculo)

    if turnos > 1:
        print(f"[benchmark] Demanda de {total} unidades em {len(cidades) - 1} "
              f"entregas: a frota de config.py foi replicada {turnos}x "
              f"({len(frota)} veiculos disponiveis).")
    return frota


def _cenario_tsp(cidades):
    """Um veiculo folgado e carga uniforme: o VRP vira o TSP do att48."""
    entregas = {c: {"prioridade": REGULAR, "demanda": 1} for c in cidades}
    frota = [Veiculo("Veiculo unico", capacidade=len(cidades),
                     autonomia=float("inf"), aceita_criticos=True)]

    config.CUSTO_FIXO_VEICULO = 0.0
    config.PESO_EQUILIBRIO = 0.0
    return entregas, frota


def _cenario_vrp(cidades):
    """A frota de config.py sobre a instancia fixa, replicada se preciso."""
    from restricoes.entregas import gerar_entregas, validar_capacidade

    entregas = gerar_entregas(cidades, config.PROB_CRITICO,
                              config.DEMANDA_MIN, config.DEMANDA_MAX)
    frota = _frota_dimensionada(cidades, entregas)

    try:
        validar_capacidade(cidades, entregas, frota)
    except ValueError as erro:
        sys.exit(str(erro) + AVISO_FROTA)
    return entregas, frota


def executar(modo: str = "tsp", geracoes: int = GERACOES_PADRAO,
             semente: int = 42) -> dict:
    random.seed(semente)

    cidades, tour_otimo = carregar(config.WIDTH, config.HEIGHT,
                                   x_offset=config.PLOT_X_OFFSET)
    otimo = comprimento_otimo(tour_otimo)

    entregas, frota = (_cenario_tsp(cidades) if modo == "tsp"
                       else _cenario_vrp(cidades))

    print(f"att48 | modo {modo} | {len(cidades)} cidades | {len(frota)} veiculo(s) "
          f"| {geracoes} geracoes | semente {semente}")
    if modo == "tsp":
        print(f"Tour otimo conhecido nesta escala: {otimo:.1f} m "
              f"({km(otimo):.2f} km)\n")
    else:
        print("Sem otimo de referencia neste modo (o problema nao e o TSP).\n")

    population = generate_random_population(cidades, config.POPULATION_SIZE)
    inicio = time.time()
    melhor_fitness = float("inf")
    melhor_individuo = population[0]

    for geracao in range(1, geracoes + 1):
        fitness = [calcular_fitness_logistico(ind, entregas, frota)
                   for ind in population]
        population, fitness = sort_population(population, fitness)

        if fitness[0] < melhor_fitness:
            melhor_fitness = fitness[0]
            melhor_individuo = population[0]

        if geracao == 1 or geracao % max(1, geracoes // 10) == 0:
            rotas = decodificar_rotas(population[0], entregas, frota)
            distancia = sum(distancia_da_rota(r) for r in rotas)
            gap = (f" | gap {100.0 * (distancia - otimo) / otimo:+.1f}%"
                   if modo == "tsp" else "")
            print(f"  geracao {geracao:>5}: custo {fitness[0]:>10.1f} | "
                  f"distancia {km(distancia):>6.2f} km{gap}")

        nova = [population[0]] if config.ELITISMO else []
        while len(nova) < config.POPULATION_SIZE:
            pai1, pai2 = selecao_por_roleta(population, fitness)
            filho = order_crossover(pai1, pai2)
            nova.append(mutate(filho, config.MUTATION_PROBABILITY))
        population = nova

    duracao = time.time() - inicio
    rotas = decodificar_rotas(melhor_individuo, entregas, frota)
    distancia = sum(distancia_da_rota(r) for r in rotas)

    print(f"\nMelhor custo: {melhor_fitness:.1f}")
    print(f"Distancia percorrida: {distancia:.1f} m ({km(distancia):.2f} km)")
    if modo == "tsp":
        print(f"Otimo conhecido: {otimo:.1f} m ({km(otimo):.2f} km)")
        print(f"Gap para o otimo: {100.0 * (distancia - otimo) / otimo:+.1f}%")
    print(f"Veiculos despachados: {sum(1 for r in rotas if len(r) > 1)} de {len(frota)}")
    print(f"Frota: {resumo_da_frota(rotas, entregas, frota)}")
    print(f"Tempo: {duracao:.1f} s ({geracoes / duracao:.0f} geracoes/s)")

    return {"modo": modo, "geracoes": geracoes, "custo": melhor_fitness,
            "distancia": distancia, "otimo": otimo if modo == "tsp" else None,
            "duracao_s": duracao}


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "tsp"
    geracoes = int(sys.argv[2]) if len(sys.argv) > 2 else GERACOES_PADRAO

    if modo not in ("tsp", "vrp"):
        sys.exit(f"Modo invalido: {modo}. Use 'tsp' ou 'vrp'.")

    executar(modo, geracoes)
