"""Funcao de custo do VRP: distancia rodada + tamanho da frota + penalidades."""

from typing import Dict, List, Sequence

import config
from restricoes.entregas import Cidade
from restricoes.roteirizacao import (carga_da_rota, decodificar_rotas,
                                  distancia_da_rota)
from restricoes.veiculo import Veiculo, km


def calcular_fitness(individual: List[Cidade], entregas: Dict[Cidade, dict],
                               veiculos: Sequence[Veiculo]) -> float:
    """
    Custo da solucao: quanto MENOR, melhor. Manter essa convencao e o que faz
    sort_population e selecao_por_roleta - que usa 1/fitness como peso da roleta
    - funcionarem sem nenhuma adaptacao.

    Todas as distancias estao em METROS (o mapa e simulado com 1 pixel = 1 m).

    Componentes:
    - soma das distancias de todas as rotas da frota (custo principal);
    - penalidade por carga acima da capacidade daquele veiculo;
    - penalidade por distancia acima da autonomia daquele veiculo;
    - custo fixo por veiculo efetivamente despachado, para atender a demanda com
      a menor frota possivel;
    - opcionalmente, penalidade pelo desequilibrio entre a maior e a menor rota.
    """
    rotas = decodificar_rotas(individual, entregas, veiculos)
    if not rotas:
        return 0.0

    distancias = [distancia_da_rota(r) for r in rotas]
    total = sum(distancias)

    for veiculo, rota, distancia in zip(veiculos, rotas, distancias):
        excesso_carga = max(0, carga_da_rota(rota, entregas) - veiculo.capacidade)
        total += excesso_carga * config.PENALIDADE_EXCESSO

        excesso_distancia = max(0.0, distancia - veiculo.autonomia)
        total += excesso_distancia * config.PENALIDADE_AUTONOMIA

    em_uso = sum(1 for rota in rotas if len(rota) > 1)
    total += em_uso * config.CUSTO_FIXO_VEICULO

    if config.PESO_EQUILIBRIO and len(distancias) > 1:
        em_uso = [d for d in distancias if d > 0]
        if len(em_uso) > 1:
            total += config.PESO_EQUILIBRIO * (max(em_uso) - min(em_uso))

    return total


def resumo_da_frota(rotas: List[List[Cidade]], entregas: Dict[Cidade, dict],
                    veiculos: Sequence[Veiculo]) -> str:
    """Linha de log com carga, entregas e uso da autonomia de cada veiculo."""
    partes = []
    for veiculo, rota in zip(veiculos, rotas):
        carga = carga_da_rota(rota, entregas)
        distancia = distancia_da_rota(rota)
        alerta = "!" if (carga > veiculo.capacidade or distancia > veiculo.autonomia) else ""
        partes.append(f"{veiculo.nome}: {carga}/{veiculo.capacidade}u "
                      f"{len(rota) - 1}ent {km(distancia):.2f}/{km(veiculo.autonomia):.2f}km{alerta}")
    return " | ".join(partes)
