"""Island mask utilities for archipelago generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
from shapely.geometry import Polygon, Point


@dataclass
class Island:
    center: np.ndarray
    radius: float


def generate_islands(num_islands: int, width: int, height: int, rng: np.random.Generator,
                     min_radius: float, max_radius: float) -> List[Island]:
    islands = []
    for _ in range(num_islands):
        cx = rng.uniform(0, width)
        cy = rng.uniform(0, height)
        r = rng.uniform(min_radius, max_radius)
        islands.append(Island(np.array([cx, cy]), r))
    return islands


def classify_land(cells: List[Polygon], islands: List[Island], sea_level: float,
                  rng: np.random.Generator) -> List[bool]:
    from noise import pnoise2
    result = []
    for poly in cells:
        centroid = np.array(poly.centroid.coords[0])
        mask = 0.0
        for isl in islands:
            d = np.linalg.norm(centroid - isl.center)
            mask = max(mask, 1 - min(1, d / isl.radius))
        noise = pnoise2(centroid[0] * 0.01, centroid[1] * 0.01, repeatx=1024, repeaty=1024, base=int(rng.integers(0, 10000)))
        val = mask + noise * 0.3
        result.append(val > sea_level)
    return result

