"""Grafico de evolucao do GA, renderizado com matplotlib dentro do Pygame."""

from typing import Tuple

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pygame

matplotlib.use("Agg")


def draw_plot(screen: pygame.Surface, x: list, y: list, x_label: str = 'Generation',
              y_label: str = 'Fitness', size: Tuple[int, int] = (400, 400),
              y2: list = None, y2_label: str = None) -> None:
    """
    Draw a plot on a Pygame screen using Matplotlib.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw the plot on.
    - x (list): The x-axis values.
    - y (list): The y-axis values.
    - x_label (str): Label for the x-axis (default is 'Generation').
    - y_label (str): Label for the y-axis (default is 'Fitness').
    - size (Tuple[int, int]): Width and height of the plot in pixels (default is (400, 400)).
    - y2 (list): Optional second series, drawn against a twin y-axis on the right.
    - y2_label (str): Label for that second axis.
    """
    dpi = 100
    fig, ax = plt.subplots(figsize=(size[0] / dpi, size[1] / dpi), dpi=dpi)
    linha_fitness, = ax.plot(x, y, color="tab:blue", label=y_label)
    ax.set_ylabel(y_label, color="tab:blue")
    ax.set_xlabel(x_label)
    ax.tick_params(axis="y", labelcolor="tab:blue")

    if y2 is not None:
        ax2 = ax.twinx()
        linha_frota, = ax2.step(x, y2, where="post", color="tab:orange",
                                linewidth=1.5, label=y2_label)
        ax2.set_ylabel(y2_label, color="tab:orange")
        ax2.tick_params(axis="y", labelcolor="tab:orange")
        if y2:
            ax2.set_ylim(0, max(y2) + 1)
            ax2.set_yticks(range(0, int(max(y2)) + 2))
        ax.legend(handles=[linha_fitness, linha_frota], loc="upper right", fontsize=8)

    plt.tight_layout()

    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    raw_data = canvas.buffer_rgba()

    size = canvas.get_width_height()
    surf = pygame.image.frombuffer(raw_data, size, "RGBA")
    screen.blit(surf, (0, 0))
    plt.close(fig)
