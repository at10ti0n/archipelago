"""River and city placement utilities.

This module implements simple river tracing and city/road placement for the
``archipelago_generator`` package. The logic mirrors the minimal approach used
in :mod:`archipelago.generator` where rivers are derived from a water flux map
and cities are positioned near coasts or rivers. Roads are built using a very
lightweight A* search connecting consecutive cities.
"""

from __future__ import annotations

from typing import List, Tuple


SEA_LEVEL = 0.26

import numpy as np


def compute_water_flux(
    elevation: np.ndarray, *, sea_level: float = SEA_LEVEL
) -> tuple[np.ndarray, np.ndarray]:
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
    water_flux: np.ndarray,
    downslope: np.ndarray,
    elevation: np.ndarray,
    *,
    min_flux: float = 3.0,
    sea_level: float = SEA_LEVEL,
) -> tuple[np.ndarray, np.ndarray, List[List[Tuple[int, int]]]]:
    """Trace river paths following downslope until reaching sea level."""

    height, width = elevation.shape
    river_map = np.zeros((height, width), dtype=int)
    river_width = np.zeros((height, width), dtype=int)
    river_id = 1
    lines: List[List[Tuple[int, int]]] = []
    visited: set[tuple[int, int]] = set()
    coords = [(y, x) for y in range(height) for x in range(width) if water_flux[y, x] >= min_flux]
    coords.sort(key=lambda p: water_flux[p], reverse=True)

    for y, x in coords:
        if (y, x) not in visited:
            cy, cx = y, x
            line: List[Tuple[int, int]] = []
            while elevation[cy, cx] >= sea_level:
                if (cy, cx) in visited:
                    break
                visited.add((cy, cx))
                river_map[cy, cx] = river_id
                river_width[cy, cx] = int(max(1, np.log2(water_flux[cy, cx])))
                line.append((cx, cy))
                ny, nx = downslope[cy, cx]
                if ny < 0 or elevation[ny, nx] < sea_level:
                    break
                cy, cx = ny, nx
            if len(line) > 1:
                lines.append(line)
            river_id += 1

    return river_map, river_width, lines




def compute_rivers(
    elevation: np.ndarray, *, sea_level: float = SEA_LEVEL
) -> tuple[np.ndarray, np.ndarray, List[List[Tuple[int, int]]]]:
    """Convenience wrapper returning ``(river_map, river_width, lines)``."""

    flux, downslope = compute_water_flux(elevation, sea_level=sea_level)
    return trace_rivers(flux, downslope, elevation, sea_level=sea_level)


