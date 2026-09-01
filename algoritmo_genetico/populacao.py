"""Operador de inicializacao: monta a populacao inicial do algoritmo genetico."""

import random
from typing import List, Tuple


def generate_random_population(cities_location: List[Tuple[float, float]], population_size: int) -> List[List[Tuple[float, float]]]:
    """
    Cria a populacao inicial embaralhando as cidades.

    Ideia: cada individuo e um "chute" de rota, ou seja, a lista de cidades
    numa ordem aleatoria. Como usamos random.sample, cada cidade aparece
    exatamente uma vez por rota - o que ja garante que nenhuma solucao nasce
    invalida (nada de cidade repetida ou faltando).

    Repetimos isso population_size vezes pra ter variedade logo de cara.
    Quanto mais diversa a populacao inicial, mais "espaco" o GA tem pra
    explorar antes de convergir.
    """
    return [random.sample(cities_location, len(cities_location)) for _ in range(population_size)]
