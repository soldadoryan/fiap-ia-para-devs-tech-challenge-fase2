"""
VRP hospitalar resolvido por algoritmo genetico, com visualizacao em Pygame.

Distribuicao de medicamentos e insumos a partir de um hospital-base, usando uma
frota heterogenea. O algoritmo busca ao mesmo tempo a menor distancia rodada e o
menor numero de veiculos despachados, respeitando prioridade da carga (criticos
antes de regulares), capacidade e autonomia de cada veiculo.

Rode com:  python vrp.py
Ajuste os parametros e a frota em config.py - nada aqui precisa ser tocado.

Feche a janela (ou aperte Q) para encerrar: o Gemini escreve o relatorio
executivo e o PDF e salvo e aberto na maquina.
"""

import itertools
import os
import random
import sys
import tempfile
import time

import pygame

import config
from algoritmo_genetico.avaliacao import sort_population
from algoritmo_genetico.cruzamento import order_crossover
from algoritmo_genetico.mutacao import mutate
from algoritmo_genetico.populacao import generate_random_population
from algoritmo_genetico.selecao import selecao_por_roleta
from restricoes.entregas import CRITICO, REGULAR, gerar_entregas, validar_capacidade
from restricoes.fitness import calcular_fitness, resumo_da_frota
from restricoes.roteirizacao import carga_da_rota, decodificar_rotas, distancia_da_rota
from restricoes.veiculo import Veiculo, km
from visualizacao.grafico import draw_plot
from visualizacao.mapa import draw_cities, draw_legend, draw_paths, draw_route_arrows
from relatorios import gerar_relatorio_final


FROTA = [Veiculo.da_config(dados) for dados in config.FROTA]

if config.SEMENTE is not None:
    random.seed(config.SEMENTE)

if config.INSTANCIA == "att48":
    from benchmarks.att48 import carregar

    cities_locations, _ = carregar(config.WIDTH, config.HEIGHT,
                                   margem=config.NODE_RADIUS,
                                   x_offset=config.PLOT_X_OFFSET)
else:
    cities_locations = [
        (random.randint(config.NODE_RADIUS + config.PLOT_X_OFFSET,
                        config.WIDTH - config.NODE_RADIUS),
         random.randint(config.NODE_RADIUS, config.HEIGHT - config.NODE_RADIUS))
        for _ in range(config.N_CITIES)
    ]

entregas = gerar_entregas(cities_locations, config.PROB_CRITICO,
                          config.DEMANDA_MIN, config.DEMANDA_MAX)
validar_capacidade(cities_locations, entregas, FROTA)

pygame.init()
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("VRP Hospitalar - Algoritmo Genetico")
clock = pygame.time.Clock()
generation_counter = itertools.count(start=1)
inicio_execucao = time.time()

population = generate_random_population(cities_locations, config.POPULATION_SIZE)
best_fitness_values = []
best_solution = []
veiculos_em_uso_values = []


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            running = False

    generation = next(generation_counter)
    screen.fill(config.BLACK)

    population_fitness = [calcular_fitness(individual, entregas, FROTA)
                          for individual in population]
    population, population_fitness = sort_population(population, population_fitness)

    best_fitness = population_fitness[0]
    best_solution = population[0]

    rotas = decodificar_rotas(best_solution, entregas, FROTA)

    best_fitness_values.append(best_fitness)
    veiculos_em_uso_values.append(sum(1 for rota in rotas if len(rota) > 1))

    draw_plot(screen, list(range(len(best_fitness_values))), best_fitness_values,
              y_label="Fitness - custo",
              size=(config.PLOT_X_OFFSET - 50, config.HEIGHT),
              y2=veiculos_em_uso_values, y2_label="Veiculos em uso")

    draw_cities(screen, [c for c in cities_locations
                         if entregas[c]["prioridade"] == REGULAR],
                config.LIGHT_BLUE, config.NODE_RADIUS)
    draw_cities(screen, [c for c in cities_locations
                         if entregas[c]["prioridade"] == CRITICO],
                config.ORANGE, config.NODE_RADIUS)

    for veiculo, rota in zip(FROTA, rotas):
        if len(rota) < 2:
            continue
        draw_paths(screen, rota, veiculo.cor, width=2)
        draw_route_arrows(screen, rota, veiculo.cor, arrow_size=12)

    draw_cities(screen, [best_solution[0]], config.GREEN, config.NODE_RADIUS)

    legend_items = [("Hospital (base)", config.GREEN),
                    ("Entrega critica", config.ORANGE),
                    ("Entrega regular", config.LIGHT_BLUE)]
    for veiculo, rota in zip(FROTA, rotas):
        marca = "*" if veiculo.aceita_criticos else " "
        legend_items.append(
            (f"{veiculo.nome}{marca} - carga {carga_da_rota(rota, entregas)}"
             f"/{veiculo.capacidade}"
             f" - {km(distancia_da_rota(rota)):.2f}/{km(veiculo.autonomia):.2f} km",
             veiculo.cor))
    legend_items.append(("* habilitado para carga critica", config.WHITE))
    draw_legend(screen, legend_items, position=(config.PLOT_X_OFFSET + 5, 5))

    print(f"Geracao {generation}: melhor custo = {round(best_fitness, 2)} | "
          f"{resumo_da_frota(rotas, entregas, FROTA)}")

    new_population = [population[0]] if config.ELITISMO else []

    while len(new_population) < config.POPULATION_SIZE:
        parent1, parent2 = selecao_por_roleta(population, population_fitness)
        child = order_crossover(parent1, parent2)
        child = mutate(child, config.MUTATION_PROBABILITY)
        new_population.append(child)

    population = new_population

    pygame.display.flip()
    clock.tick(config.FPS)


captura = os.path.join(tempfile.gettempdir(), "vrp_melhor_rota.png")
try:
    pygame.image.save(screen, captura)
except Exception as erro:
    print(f"[vrp] Nao foi possivel salvar a captura da tela: {erro}")
    captura = None

gerar_relatorio_final(cities_locations, entregas, FROTA, best_solution,
                      best_fitness_values,
                      duracao_segundos=time.time() - inicio_execucao,
                      abrir=config.ABRIR_PDF_AO_FINAL,
                      imagem_tela=captura)

pygame.quit()
sys.exit()
