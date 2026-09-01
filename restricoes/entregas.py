"""Dados de entrega de cada ponto do mapa e checagem do porte da frota."""

import random
from typing import Dict, List, Sequence, Tuple

from restricoes.veiculo import Veiculo

Cidade = Tuple[float, float]

CRITICO = "critico"
REGULAR = "regular"


def gerar_entregas(cities_locations: List[Cidade],
                   prob_critico: float = 0.3,
                   demanda_min: int = 1,
                   demanda_max: int = 10) -> Dict[Cidade, dict]:
    """
    Sorteia os dados de entrega de cada cidade.

    Estes parametros descrevem a CARGA, nao o veiculo: a demanda de um ponto e a
    urgencia do que ele pede existem antes de qualquer veiculo ser escolhido.

    As cidades sao tuplas (x, y), ou seja, hashaveis - da pra pendurar atributos
    nelas num dicionario sem mexer na representacao usada pelo GA.

    Cada cidade recebe:
    - prioridade: CRITICO (medicamento critico) ou REGULAR (insumo comum);
    - demanda: quanto de carga aquela entrega ocupa no veiculo.
    """
    entregas = {}
    for city in cities_locations:
        entregas[city] = {
            "prioridade": CRITICO if random.random() < prob_critico else REGULAR,
            "demanda": random.randint(demanda_min, demanda_max),
        }
    return entregas


def demanda_total(cities_locations: List[Cidade], entregas: Dict[Cidade, dict],
                  prioridade: str = None) -> int:
    """
    Soma a carga das entregas (a base nao conta como entrega).

    Passando `prioridade`, soma so as entregas daquele tipo.
    """
    if not cities_locations:
        return 0
    base = cities_locations[0]
    return sum(dados["demanda"] for c, dados in entregas.items()
               if c != base and (prioridade is None or dados["prioridade"] == prioridade))


def validar_capacidade(cities_locations: List[Cidade], entregas: Dict[Cidade, dict],
                       veiculos: Sequence[Veiculo], folga_minima: float = 1.3) -> None:
    """
    Confere na inicializacao se a frota consegue atender toda a demanda.

    Duas checagens: a capacidade total da frota, e a capacidade so dos veiculos
    habilitados a levar medicamento critico. Um alerta e emitido quando a folga e
    pequena: o split e guloso, e sem alguma folga ele nao consegue empacotar tudo
    sem estourar a capacidade, o que faria o fitness cair na penalidade sempre.
    """
    if not veiculos:
        raise ValueError("A frota esta vazia: defina pelo menos um Veiculo.")

    total = demanda_total(cities_locations, entregas)
    disponivel = sum(v.capacidade for v in veiculos)

    if disponivel < total:
        raise ValueError(
            f"Frota subdimensionada: demanda total = {total}, capacidade da frota = "
            f"{disponivel} ({len(veiculos)} veiculos). Aumente a capacidade ou "
            f"adicione veiculos em FROTA."
        )

    total_critico = demanda_total(cities_locations, entregas, CRITICO)
    disponivel_critico = sum(v.capacidade for v in veiculos if v.aceita_criticos)

    if disponivel_critico < total_critico:
        raise ValueError(
            f"Nenhuma folga para medicamentos criticos: demanda critica = {total_critico}, "
            f"capacidade habilitada = {disponivel_critico}. Habilite aceita_criticos em "
            f"mais veiculos de FROTA."
        )

    if disponivel < total * folga_minima:
        print(f"[AVISO] Folga de capacidade baixa ({disponivel / total:.2f}x). "
              f"Recomendado pelo menos {folga_minima:.2f}x para o split guloso "
              f"acomodar as entregas sem penalidade.")
