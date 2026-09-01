"""O veiculo da frota e as unidades de medida do mapa simulado."""

from dataclasses import dataclass, field
from typing import Tuple

import config


@dataclass
class Veiculo:
    """
    Um veiculo da frota, com caracteristicas proprias.

    - nome: identificacao usada no log e na legenda da tela;
    - capacidade: quanto de carga cabe nele;
    - autonomia: distancia maxima (em metros) que ele consegue rodar num turno;
    - aceita_criticos: se ele e habilitado a transportar medicamento critico
      (refrigeracao / certificacao). Veiculo sem essa habilitacao so recebe
      insumo regular;
    - cor: cor da rota dele no desenho.
    """
    nome: str
    capacidade: int
    autonomia: float
    aceita_criticos: bool = True
    cor: Tuple[int, int, int] = field(default=(0, 0, 255))

    @classmethod
    def da_config(cls, dados: dict) -> "Veiculo":
        """Constroi um veiculo a partir de um dicionario de config.FROTA."""
        return cls(**dados)


def km(distancia_m: float) -> float:
    """Converte a distancia interna (metros) para km, usada so na apresentacao."""
    return distancia_m * config.METROS_POR_PIXEL / 1000.0
