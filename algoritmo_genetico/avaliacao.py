"""Medidas basicas usadas pelo algoritmo genetico: distancia e ordenacao."""

import math
from typing import List, Tuple

Ponto = Tuple[float, float]


def calculate_distance(point1: Ponto, point2: Ponto) -> float:
    """Distancia euclidiana entre dois pontos: o velho Pitagoras."""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def sort_population(population: List[List[Ponto]],
                    fitness: List[float]) -> Tuple[List[List[Ponto]], List[float]]:
    """
    Ordena a populacao do melhor individuo (menor custo) para o pior.

    Junta populacao e fitness em pares, ordena pelo fitness e separa de novo. E
    isso que permite o elitismo saber quem sao os melhores.
    """
    combined_lists = list(zip(population, fitness))
    sorted_combined_lists = sorted(combined_lists, key=lambda x: x[1])
    sorted_population, sorted_fitness = zip(*sorted_combined_lists)

    return sorted_population, sorted_fitness
