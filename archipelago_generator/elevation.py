"""Elevation generation and simple erosion."""

from __future__ import annotations

from typing import List

import numpy as np
from perlin_noise import PerlinNoise
from shapely.geometry import Polygon


def assign_elevation(cells: List[Polygon], land_mask: List[bool], rng: np.random.Generator) -> np.ndarray:
    """Assign elevation using shared Perlin noise for smoother results."""

    noise = PerlinNoise(seed=int(rng.integers(0, 10000)))
    elev = np.zeros(len(cells))
    for i, poly in enumerate(cells):
        centroid = poly.centroid
        val = noise([centroid.x * 0.02, centroid.y * 0.02])
        base = (val + 1) / 2
        elev[i] = base if land_mask[i] else 0.0
    return elev

