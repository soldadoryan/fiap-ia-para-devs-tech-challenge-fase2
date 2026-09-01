"""
Consolidacao dos numeros da rodada.

Este modulo e a unica fonte de numeros do relatorio: distancias, cargas e
percentuais sao calculados aqui e reaproveitados tanto pelo prompt do Gemini
quanto pelo anexo de conferencia do PDF. O LLM nunca inventa valor.
"""

from datetime import datetime
from typing import Dict, List, Sequence

from algoritmo_genetico.avaliacao import calculate_distance
from restricoes.entregas import CRITICO
from restricoes.roteirizacao import (carga_da_rota, decodificar_rotas,
                                  distancia_da_rota)
import config
from restricoes.veiculo import Veiculo, km as _km


def _minutos(distancia_km: float) -> float:
    """Tempo de rota estimado, em minutos, para uma distancia em km."""
    return 60.0 * distancia_km / config.VELOCIDADE_MEDIA_KMH


def montar_dados_execucao(cities_locations: List[tuple], entregas: Dict[tuple, dict],
                          veiculos: Sequence[Veiculo], best_solution: List[tuple],
                          best_fitness_values: List[float],
                          duracao_segundos: float) -> dict:
    """
    Consolida o resultado da rodada num dicionario pronto pra virar JSON.

    E este dicionario que alimenta tanto o prompt do Gemini quanto o anexo de
    conferencia do PDF.
    """
    rotas = decodificar_rotas(best_solution, entregas, veiculos)
    base = best_solution[0]

    fitness_inicial = best_fitness_values[0] if best_fitness_values else 0.0
    fitness_final = best_fitness_values[-1] if best_fitness_values else 0.0
    melhoria = (100.0 * (fitness_inicial - fitness_final) / fitness_inicial
                if fitness_inicial else 0.0)

    dados_veiculos = []
    for veiculo, rota in zip(veiculos, rotas):
        distancia = distancia_da_rota(rota)
        carga = carga_da_rota(rota, entregas)

        paradas = []
        for ordem, cidade in enumerate(rota[1:], start=1):
            anterior = rota[ordem - 1]
            paradas.append({
                "ordem": ordem,
                "coordenada": [int(cidade[0]), int(cidade[1])],
                "prioridade": entregas[cidade]["prioridade"],
                "carga": entregas[cidade]["demanda"],
                "distancia_do_ponto_anterior_km": round(_km(calculate_distance(anterior, cidade)), 2),
            })

        dados_veiculos.append({
            "nome": veiculo.nome,
            "capacidade": veiculo.capacidade,
            "autonomia_km": round(_km(veiculo.autonomia), 2),
            "habilitado_carga_critica": veiculo.aceita_criticos,
            "carga_transportada": carga,
            "ocupacao_percentual": round(100.0 * carga / veiculo.capacidade, 1) if veiculo.capacidade else 0.0,
            "n_entregas": len(rota) - 1,
            "n_entregas_criticas": sum(1 for c in rota[1:]
                                       if entregas[c]["prioridade"] == CRITICO),
            "distancia_km": round(_km(distancia), 2),
            "uso_autonomia_percentual": round(100.0 * distancia / veiculo.autonomia, 1) if veiculo.autonomia else 0.0,
            "tempo_estimado_min": round(_minutos(_km(distancia)), 1),
            "excedeu_autonomia": distancia > veiculo.autonomia,
            "excedeu_capacidade": carga > veiculo.capacidade,
            "paradas": paradas,
        })

    distancia_total = sum(v["distancia_km"] for v in dados_veiculos)

    return {
        "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "resumo": {
            "n_pontos_entrega": len(cities_locations) - 1,
            "base_hospital": [int(base[0]), int(base[1])],
            "n_veiculos_frota": len(veiculos),
            "n_veiculos_em_uso": sum(1 for v in dados_veiculos if v["n_entregas"] > 0),
            "veiculos_ociosos": [v["nome"] for v in dados_veiculos if v["n_entregas"] == 0],
            "geracoes_executadas": len(best_fitness_values),
            "duracao_execucao_s": round(duracao_segundos, 1),
            "fitness_inicial": round(fitness_inicial, 1),
            "fitness_final": round(fitness_final, 1),
            "melhoria_percentual": round(melhoria, 1),
            "distancia_total_km": round(distancia_total, 2),
            "tempo_total_estimado_min": round(_minutos(distancia_total), 1),
            "carga_total_transportada": sum(v["carga_transportada"] for v in dados_veiculos),
            "entregas_criticas": sum(v["n_entregas_criticas"] for v in dados_veiculos),
        },
        "veiculos": dados_veiculos,
    }
