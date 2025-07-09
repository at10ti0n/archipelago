"""River and city placement utilities.

This module implements simple river tracing and city/road placement for the
``archipelago_generator`` package. The logic mirrors the minimal approach used
in :mod:`archipelago.generator` where rivers are derived from a water flux map
and cities are positioned near coasts or rivers. Roads are built using a very
lightweight A* search connecting consecutive cities.
"""

from __future__ import annotations

import heapq
from typing import List, Tuple

SEA_LEVEL = 0.26

import numpy as np


def compute_water_flux(elevation: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute water flux and downslope for each tile.

    Parameters
    ----------
    elevation : np.ndarray
        Normalized elevation grid (0..1).

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        ``(water_flux, downslope)`` arrays.
    """

    height, width = elevation.shape
    downslope = np.full((height, width, 2), -1, dtype=int)
    for y in range(height):
        for x in range(width):
            min_elev = elevation[y, x]
            best: tuple[int, int] | None = None
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx < width and elevation[ny, nx] < min_elev:
                    min_elev = elevation[ny, nx]
                    best = (ny, nx)
            if best is not None:
                downslope[y, x] = best

    water_flux = np.ones((height, width))
    order = [(y, x) for y in range(height) for x in range(width)]
    order.sort(key=lambda p: -elevation[p])
    for y, x in order:
        ny, nx = downslope[y, x]
        if ny >= 0:
            water_flux[ny, nx] += water_flux[y, x]

    return water_flux, downslope


def trace_rivers(
    water_flux: np.ndarray, downslope: np.ndarray, elevation: np.ndarray, *, min_flux: float = 20.0
) -> tuple[np.ndarray, np.ndarray]:
    """Trace river paths following downslope until reaching sea level."""

    height, width = elevation.shape
    river_map = np.zeros((height, width), dtype=int)
    river_width = np.zeros((height, width), dtype=int)
    river_id = 1
    visited: set[tuple[int, int]] = set()

    for y in range(height):
        for x in range(width):
            if water_flux[y, x] >= min_flux and (y, x) not in visited:
                cy, cx = y, x
                while elevation[cy, cx] >= SEA_LEVEL:
                    if (cy, cx) in visited:
                        break
                    visited.add((cy, cx))
                    river_map[cy, cx] = river_id
                    river_width[cy, cx] = int(max(1, np.log2(water_flux[cy, cx])))
                    ny, nx = downslope[cy, cx]
                    if ny < 0 or elevation[ny, nx] < SEA_LEVEL:
                        break
                    cy, cx = ny, nx
                river_id += 1

    return river_map, river_width


def place_cities(
    river_map: np.ndarray, elevation: np.ndarray, *, n_cities: int = 3, min_dist: int = 10
) -> List[Tuple[int, int]]:
    """Place cities near rivers or coasts with spacing."""

    height, width = elevation.shape
    candidates: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            if SEA_LEVEL < elevation[y, x] < 0.8:
                if river_map[y, x] > 0 or any(
                    0 <= y + dy < height and 0 <= x + dx < width and elevation[y + dy, x + dx] < SEA_LEVEL
                    for dy in [-1, 0, 1]
                    for dx in [-1, 0, 1]
                ):
                    candidates.append((y, x))

    rng = np.random.default_rng(0)
    rng.shuffle(candidates)
    cities: list[tuple[int, int]] = []
    for c in candidates:
        if all(np.hypot(c[0] - y, c[1] - x) >= min_dist for y, x in cities):
            cities.append(c)
        if len(cities) == n_cities:
            break
    return cities


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


def build_roads(cities: List[Tuple[int, int]], elevation: np.ndarray) -> np.ndarray:
    """Connect consecutive cities using A* to create roads."""

    height, width = elevation.shape
    road = np.zeros((height, width), dtype=bool)
    if len(cities) < 2:
        return road

    cost = 1.0 + elevation * 3.0
    cost[elevation < SEA_LEVEL] = 1e6
    for a, b in zip(cities[:-1], cities[1:]):
        path = _astar(a, b, cost)
        for y, x in path:
            road[y, x] = True
    return road


def compute_rivers(elevation: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Convenience wrapper returning ``(river_map, river_width)``."""

    flux, downslope = compute_water_flux(elevation)
    return trace_rivers(flux, downslope, elevation)


