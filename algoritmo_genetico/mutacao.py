"""Operador de mutacao: troca de cidades vizinhas na rota."""

import copy
import random
from typing import List, Tuple


def mutate(solution: List[Tuple[float, float]], mutation_probability: float) -> List[Tuple[float, float]]:
    """
    Mutacao por troca de vizinhos (swap).

    A mutacao e o "empurraozinho" pro GA nao ficar preso sempre na mesma
    solucao. Sem ela, depois de algumas geracoes a populacao vira copia da
    copia e para de melhorar.

    Como funciona aqui:
    - Joga um dado (random.random). Se cair abaixo da mutation_probability,
      a mutacao acontece; se nao, a rota volta igualzinha.
    - Rota com menos de 2 cidades nao tem o que trocar, entao sai fora.
    - Sorteia uma posicao e troca aquela cidade com a cidade seguinte.

    Repare que trabalhamos numa copia (deepcopy): a rota original nao e
    alterada, o que evita baguncar individuos que ainda estao na populacao.
    """
    mutated_solution = copy.deepcopy(solution)

    if random.random() < mutation_probability:

        if len(solution) < 2:
            return solution

        index = random.randint(0, len(solution) - 2)

        mutated_solution[index], mutated_solution[index + 1] = solution[index + 1], solution[index]

    return mutated_solution
