"""
Regras do VRP hospitalar: frota heterogenea, prioridades e capacidade.

A ideia central deste pacote e que o cromossomo do algoritmo genetico NAO muda:
ele e uma permutacao simples de todos os pontos do mapa. Os operadores geneticos
(populacao inicial, cruzamento, mutacao, selecao) funcionam sobre ele sem saber
nada de logistica.

O que este pacote acrescenta e a LEITURA desse cromossomo. Um decodificador
traduz a permutacao em rotas concretas de uma frota:

    permutacao  ->  decodificar_rotas()  ->  [rota_veic_1, ..., rota_veic_N]

Como o decodificador e deterministico, o mesmo cromossomo sempre gera as mesmas
rotas - o GA continua otimizando normalmente, so que agora e avaliado pelo
resultado ja decodificado (capacidade, autonomia e prioridade respeitadas).

- veiculo.py       -> o que e um veiculo da frota
- entregas.py      -> demanda e prioridade de cada ponto, e a validacao da frota
- roteirizacao.py  -> decodificador da permutacao em rotas
- fitness.py       -> quanto custa a solucao decodificada
"""
