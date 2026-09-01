"""Operadores de selecao: quem vira pai da proxima geracao."""

import random
from typing import List, Tuple

import numpy as np


def selecao_por_roleta(population: List[List[Tuple[float, float]]], population_fitness: List[float]) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
    """
    Selecao proporcional ao fitness, a famosa "roleta viciada".

    Imagina uma roleta de cassino em que cada individuo ganha uma fatia. Quem
    tem rota mais curta ganha uma fatia maior, entao tem mais chance de ser
    sorteado - mas os ruins ainda tem uma chance pequena, e isso e proposital:
    mantem diversidade e evita o GA travar num otimo local.

    O pulo do gato e o 1/fitness: aqui fitness e distancia, ou seja, quanto
    MENOR melhor. Invertendo, a rota curta vira o peso grande da roleta.

    Devolve dois pais (podem ser o mesmo individuo, igual no sorteio original).
    """
    probability = 1 / np.array(population_fitness)
    parent1, parent2 = random.choices(population, weights=probability, k=2)
    return parent1, parent2
