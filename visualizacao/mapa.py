"""Desenho do mapa: pontos de entrega, rotas da frota, setas e legenda."""

import math
from typing import List, Tuple

import pygame


def draw_cities(screen: pygame.Surface, cities_locations: List[Tuple[int, int]], rgb_color: Tuple[int, int, int], node_radius: int) -> None:
    """
    Draws circles representing cities on the given Pygame screen.

    Parameters:
    - screen (pygame.Surface): The Pygame surface on which to draw the cities.
    - cities_locations (List[Tuple[int, int]]): List of (x, y) coordinates representing the locations of cities.
    - rgb_color (Tuple[int, int, int]): Tuple of three integers (R, G, B) representing the color of the city circles.
    - node_radius (int): The radius of the city circles.

    Returns:
    None
    """
    for city_location in cities_locations:
        pygame.draw.circle(screen, rgb_color, city_location, node_radius)



def draw_paths(screen: pygame.Surface, path: List[Tuple[int, int]], rgb_color: Tuple[int, int, int], width: int = 1):
    """
    Draw a path on a Pygame screen.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw the path on.
    - path (List[Tuple[int, int]]): List of tuples representing the coordinates of the path.
    - rgb_color (Tuple[int, int, int]): RGB values for the color of the path.
    - width (int): Width of the path lines (default is 1).
    """
    pygame.draw.lines(screen, rgb_color, True, path, width=width)


def draw_route_arrows(screen: pygame.Surface, path: List[Tuple[int, int]],
                      rgb_color: Tuple[int, int, int], arrow_size: int = 9,
                      closed: bool = True) -> None:
    """
    Draw arrowheads along a route to indicate travel direction.

    One arrowhead is drawn at the middle of each segment, pointing from the
    current city to the next one. The final segment (back to the start) is
    included when `closed` is True.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw on.
    - path (List[Tuple[int, int]]): Ordered coordinates of the route.
    - rgb_color (Tuple[int, int, int]): Color of the arrowheads.
    - arrow_size (int): Length of the arrowhead in pixels (default is 9).
    - closed (bool): Whether the route returns to its first point (default True).
    """
    n = len(path)
    if n < 2:
        return

    n_segments = n if closed else n - 1

    for i in range(n_segments):
        start = path[i]
        end = path[(i + 1) % n]

        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0:
            continue

        ux, uy = dx / length, dy / length
        px, py = -uy, ux

        mx = start[0] + dx * 0.5
        my = start[1] + dy * 0.5

        tip = (mx + ux * arrow_size * 0.5, my + uy * arrow_size * 0.5)
        base_x = mx - ux * arrow_size * 0.5
        base_y = my - uy * arrow_size * 0.5
        half_width = arrow_size * 0.4

        left = (base_x + px * half_width, base_y + py * half_width)
        right = (base_x - px * half_width, base_y - py * half_width)

        pygame.draw.polygon(screen, rgb_color, [tip, left, right])


def draw_legend(screen: pygame.Surface, items: List[Tuple[str, Tuple[int, int, int]]],
                position: Tuple[int, int], node_radius: int = 6) -> None:
    """
    Draw a color legend on a Pygame screen.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw the legend on.
    - items (List[Tuple[str, Tuple[int, int, int]]]): List of (label, rgb_color) pairs.
    - position (Tuple[int, int]): Top-left (x, y) coordinate of the legend box.
    - node_radius (int): Radius of the color sample circles (default is 6).
    """
    pygame.font.init()

    font_size = 14
    my_font = pygame.font.SysFont('Arial', font_size)
    line_height = font_size + 6
    padding = 6

    labels = [my_font.render(label, True, (255, 255, 255)) for label, _ in items]
    box_width = padding * 2 + 2 * node_radius + 8 + max(l.get_width() for l in labels)
    box_height = padding * 2 + line_height * len(items)

    x, y = position
    background = pygame.Surface((box_width, box_height))
    background.fill((0, 0, 0))
    background.set_alpha(220)
    screen.blit(background, (x, y))
    pygame.draw.rect(screen, (255, 255, 255), (x, y, box_width, box_height), 1)

    for index, ((_, rgb_color), label_surface) in enumerate(zip(items, labels)):
        line_y = y + padding + index * line_height + line_height // 2
        pygame.draw.circle(screen, rgb_color,
                           (x + padding + node_radius, line_y), node_radius)
        screen.blit(label_surface,
                    (x + padding + 2 * node_radius + 8, line_y - font_size // 2 - 1))
