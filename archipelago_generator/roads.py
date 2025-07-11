"""Road generation utilities with optional Perlin noise distortion."""

from __future__ import annotations

from typing import List, Tuple
import heapq

import numpy as np
from perlin_noise import PerlinNoise
from shapely.geometry import LineString

SEA_LEVEL = 0.26


def _astar(start: tuple[int, int], goal: tuple[int, int], cost_grid: np.ndarray) -> List[Tuple[int, int]]:
    """Simple A* search on a 4-neighbour grid."""

    height, width = cost_grid.shape
    open_set: list[tuple[float, tuple[int, int]]] = []
    heapq.heappush(open_set, (0.0, start))
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g: dict[tuple[int, int], float] = {start: 0.0}

    def heur(a: tuple[int, int], b: tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            break
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = current[0] + dy, current[1] + dx
            if not (0 <= ny < height and 0 <= nx < width):
                continue
            new_cost = g[current] + cost_grid[ny, nx]
            if (ny, nx) not in g or new_cost < g[(ny, nx)]:
                g[(ny, nx)] = new_cost
                priority = new_cost + heur((ny, nx), goal)
                heapq.heappush(open_set, (priority, (ny, nx)))
                came_from[(ny, nx)] = current

    path: list[tuple[int, int]] = []
    cur = goal
    if cur not in came_from and cur != start:
        return path
    while cur != start:
        path.append(cur)
        cur = came_from[cur]
    path.append(start)
    path.reverse()
    return path


def _distort_line(line: LineString, noise: PerlinNoise, *, amplitude: float, frequency: float) -> LineString:
    """Return a distorted copy of ``line`` using 1D noise."""
    if line.length == 0:
        return line
    (x1, y1), (x2, y2) = line.coords[0], line.coords[-1]
    vec = np.array([x2 - x1, y2 - y1])
    norm = np.array([-vec[1], vec[0]])
    if np.allclose(norm, 0):
        return line
    norm = norm / np.linalg.norm(norm)
    steps = max(int(line.length / 5), 2)
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = x1 + vec[0] * t
        y = y1 + vec[1] * t
        offset = noise(t * frequency) * amplitude
        pts.append((x + norm[0] * offset, y + norm[1] * offset))
    return LineString(pts)


def build_roads(
    cities: List[Tuple[int, int]],
    elevation: np.ndarray,
    *,
    sea_level: float = SEA_LEVEL,
    noise_amplitude: float = 1.0,
    noise_frequency: float = 0.15,
    seed: int = 0,
) -> np.ndarray:
    """Connect consecutive cities using A* to create roads.

    The resulting paths are lightly distorted using 1D Perlin noise to avoid
    perfectly straight segments.
    """

    height, width = elevation.shape
    road = np.zeros((height, width), dtype=bool)
    if len(cities) < 2:
        return road

    cost = 1.0 + elevation * 3.0
    cost[elevation < sea_level] = 1e6

    noise = PerlinNoise(seed=seed)

    for a, b in zip(cities[:-1], cities[1:]):
        path = _astar(a, b, cost)
        if len(path) < 2:
            continue
        line = LineString([(x, y) for y, x in path])
        line = _distort_line(
            line,
            noise,
            amplitude=noise_amplitude,
            frequency=noise_frequency,
        )

        length = line.length
        d = 0.0
        while d <= length:
            pt = line.interpolate(d)
            x = int(round(pt.x))
            y = int(round(pt.y))
            if 0 <= y < height and 0 <= x < width and elevation[y, x] >= sea_level:
                road[y, x] = True
            d += 1.0
    return road
