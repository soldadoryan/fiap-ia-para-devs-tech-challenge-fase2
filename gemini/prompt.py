"""
Montagem do prompt enviado ao Gemini.

O texto do prompt NAO fica em codigo: ele mora em prompt.md, ao lado deste
arquivo, para poder ser lido e ajustado sem mexer em Python. Este modulo so
carrega o arquivo e substitui os marcadores.

Marcadores disponiveis no prompt.md:

    {{VELOCIDADE_MEDIA_KMH}}  velocidade media usada na estimativa de tempo
    {{DADOS_JSON}}            os numeros da rodada, ja calculados, em JSON
"""

import json
import os

import config

CAMINHO_PROMPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.md")


def carregar_modelo_de_prompt(caminho: str = None) -> str:
    """Le o prompt.md cru, sem substituir nenhum marcador."""
    with open(caminho or CAMINHO_PROMPT, encoding="utf-8") as arquivo:
        return arquivo.read()


def montar_prompt(dados: dict, caminho: str = None) -> str:
    """
    Monta o prompt final a partir do prompt.md e dos dados da rodada.

    A substituicao e feita com str.replace, e nao com str.format: o JSON dos
    dados esta cheio de chaves, que o format tentaria interpretar.
    """
    modelo = carregar_modelo_de_prompt(caminho)
    return (modelo
            .replace("{{VELOCIDADE_MEDIA_KMH}}", f"{config.VELOCIDADE_MEDIA_KMH:.0f}")
            .replace("{{DADOS_JSON}}", json.dumps(dados, ensure_ascii=False, indent=2)))
