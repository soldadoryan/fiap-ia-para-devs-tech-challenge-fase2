"""
Parametros e dados mockados da simulacao. Unico arquivo que se mexe pra rodar
cenarios diferentes - nenhum modulo do algoritmo precisa ser tocado.

De proposito este arquivo NAO importa nada do projeto: e configuracao pura, o
que evita qualquer dependencia circular com os pacotes que o consomem.
"""

WIDTH, HEIGHT = 1600, 900
NODE_RADIUS = 10
FPS = 30
PLOT_X_OFFSET = 800

METROS_POR_PIXEL = 1.0
VELOCIDADE_MEDIA_KMH = 60.0

INSTANCIA = "aleatoria" # att48 | aleatoria
SEMENTE = None

N_CITIES = 30
POPULATION_SIZE = 100
MUTATION_PROBABILITY = 0.5
ELITISMO = True

PROB_CRITICO = 0.5
DEMANDA_MIN = 1
DEMANDA_MAX = 10

PENALIDADE_EXCESSO = 1000.0
PENALIDADE_AUTONOMIA = 5.0
CUSTO_FIXO_VEICULO = 800.0

PESO_EQUILIBRIO = 0.0

FROTA = [
    {"nome": "Ambulancia",      "capacidade": 40, "autonomia": 3500,
     "aceita_criticos": True,  "cor": (200, 0, 0)},
    {"nome": "Van refrigerada", "capacidade": 70, "autonomia": 4500,
     "aceita_criticos": True,  "cor": (0, 0, 255)},
    {"nome": "Furgao",          "capacidade": 60, "autonomia": 3000,
     "aceita_criticos": False, "cor": (0, 150, 150)},
    {"nome": "Utilitario",      "capacidade": 50, "autonomia": 2500,
     "aceita_criticos": False, "cor": (200, 0, 200)},
]

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
ORANGE = (255, 140, 0)
LIGHT_BLUE = (100, 170, 230)

MODELO_GEMINI = "gemini-3.5-flash"
MODELOS_GEMINI_ALTERNATIVOS = ["gemini-flash-latest", "gemini-flash-lite-latest"]
TENTATIVAS_GEMINI = 3
ESPERA_INICIAL_S = 4
ABRIR_PDF_AO_FINAL = True

PASTA_RELATORIOS = "relatorios"
