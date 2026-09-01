"""
Instancia att48: 48 capitais dos EUA, benchmark classico de TSP.

Fonte dos dados: https://people.sc.fsu.edu/~jburkardt/datasets/tsp/tsp.html

Serve a dois propositos aqui:

1. Instancia FIXA e reprodutivel - trocar o sorteio aleatorio por um mapa
   sempre igual e o que permite comparar parametros e versoes do algoritmo.
2. Referencia de qualidade - a ordem otima do tour e conhecida, entao da pra
   medir o quanto o GA ficou longe do otimo.

Atencao ao ponto 2: o otimo conhecido e de um TSP puro (um unico veiculo, sem
capacidade, sem autonomia e sem custo de frota). A comparacao so faz sentido com
a frota reduzida a um veiculo folgado - e exatamente o que o runner em
benchmarks/__main__.py monta. Com a frota hospitalar completa o problema e
outro, e o numero otimo do TSP nao serve de referencia.

O otimo publicado de 10628 usa a distancia pseudo-euclidiana ATT, que nao e a
que este projeto calcula. Por isso nao usamos numero de tabela: a funcao
comprimento_otimo() mede o tour otimo com a MESMA distancia euclidiana do
projeto, o que torna a comparacao honesta.
"""

from typing import List, Tuple

from algoritmo_genetico.avaliacao import calculate_distance

ATT48_COORDENADAS = [(6734, 1453),
(2233 , 10),
(5530, 1424),
 (401, 841),
(3082, 1644),
(7608, 4458),
(7573, 3716),
(7265, 1268),
(6898, 1885),
(1112, 2049),
(5468, 2606),
(5989, 2873),
(4706, 2674),
(4612, 2035),
(6347, 2683),
(6107, 669),
(7611, 5184),
(7462, 3590),
(7732, 4723),
(5900, 3561),
(4483, 3369),
(6101, 1110),
(5199, 2182),
(1633, 2809),
(4307, 2322),
 (675, 1006),
(7555, 4819),
(7541, 3981),
(3177, 756),
(7352, 4506),
(7545, 2801),
(3245, 3305),
(6426, 3173),
(4608, 1198),
 (23, 2216),
(7248, 3779),
(7762, 4595),
(7392, 2244),
(3484, 2829),
(6271, 2135),
(4985, 140),
(1916, 1569),
(7280, 4899),
(7509, 3239),
 (10, 2676),
(6807, 2993),
(5185, 3258),
(3023, 1942)]

ATT48_ORDEM_OTIMA = [1,
8,
38,
31,
44,
18,
7,
28,
6,
37,
19,
27,
17,
43,
30,
36,
46,
33,
20,
47,
21,
32,
39,
48,
5,
42,
24,
10,
45,
35,
4,
26,
2,
29,
34,
41,
16,
22,
3,
23,
14,
25,
13,
11,
12,
15,
40,
9,
1,]

def carregar(largura: int, altura: int, margem: int = 10,
             x_offset: int = 0) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Escala as 48 cidades para caberem na area de desenho.

    Devolve (cidades, tour_otimo): a lista de pontos ja em coordenadas de tela e
    o tour otimo conhecido, nos mesmos pontos, pronto para comparacao.

    - largura/altura: tamanho da area util de desenho, em pixels;
    - x_offset: deslocamento horizontal (no simulador o mapa comeca depois do
      grafico, entao os pontos nao podem nascer na metade esquerda da tela);
    - margem: folga nas bordas para os circulos nao serem cortados.
    """
    max_x = max(p[0] for p in ATT48_COORDENADAS)
    max_y = max(p[1] for p in ATT48_COORDENADAS)

    escala_x = (largura - x_offset - 2 * margem) / max_x
    escala_y = (altura - 2 * margem) / max_y

    cidades = [(int(p[0] * escala_x + x_offset + margem),
                int(p[1] * escala_y + margem)) for p in ATT48_COORDENADAS]

    ordem = ATT48_ORDEM_OTIMA[:-1] if ATT48_ORDEM_OTIMA[-1] == ATT48_ORDEM_OTIMA[0]         else ATT48_ORDEM_OTIMA
    tour_otimo = [cidades[i - 1] for i in ordem]
    return cidades, tour_otimo


def comprimento_otimo(tour_otimo: List[Tuple[int, int]]) -> float:
    """
    Comprimento do tour otimo conhecido, medido com a distancia euclidiana do
    projeto e ja na escala da tela - ou seja, na mesma unidade em que o GA e
    avaliado. E este numero que serve de linha de base.
    """
    n = len(tour_otimo)
    return sum(calculate_distance(tour_otimo[i], tour_otimo[(i + 1) % n])
               for i in range(n))
