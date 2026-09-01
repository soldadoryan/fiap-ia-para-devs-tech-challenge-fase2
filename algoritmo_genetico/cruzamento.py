"""Operador de cruzamento (crossover): Order Crossover (OX)."""

import random
from typing import List, Tuple


def order_crossover(parent1: List[Tuple[float, float]], parent2: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Order Crossover (OX): mistura dois pais sem repetir cidade.

    Numa rota nao da pra cortar e colar pedaco dos pais igual crossover comum,
    senao a rota filha acabaria com cidade repetida e outra sumida. O OX
    resolve isso assim:

    1. Sorteia uma fatia do pai 1 (do start_index ate o end_index) e copia
       ela inteira pro filho. Esse pedaco ja fica "reservado".
    2. Olha as posicoes que sobraram (o que estava fora da fatia).
    3. Percorre o pai 2 na ordem dele e pega so as cidades que ainda nao
       entraram no filho.
    4. Vai encaixando essas cidades nos buracos, respeitando a ordem em que
       aparecem no pai 2.

    Resultado: o filho herda um trecho de rota do pai 1 e a ordem relativa do
    resto vem do pai 2 - e continua sendo uma rota valida.
    """
    length = len(parent1)

    start_index = random.randint(0, length - 1)
    end_index = random.randint(start_index + 1, length)

    child = parent1[start_index:end_index]

    remaining_positions = [i for i in range(length) if i < start_index or i >= end_index]
    remaining_genes = [gene for gene in parent2 if gene not in child]

    for position, gene in zip(remaining_positions, remaining_genes):
        child.insert(position, gene)

    return child
