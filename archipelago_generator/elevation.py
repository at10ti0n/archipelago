"""Elevation generation and simple erosion."""

from __future__ import annotations

from typing import List

import numpy as np
from perlin_noise import PerlinNoise
from shapely.geometry import Polygon


def _fractal_noise(noise: PerlinNoise, x: float, y: float, *, octaves: int = 4,
                   lacunarity: float = 2.0, persistence: float = 0.5) -> float:
    """Return fractal noise value in range [-1, 1]."""
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    for _ in range(octaves):
        value += amplitude * noise([x * frequency, y * frequency])
        amplitude *= persistence
        frequency *= lacunarity
    return value


def assign_elevation(cells: List[Polygon], width: int, height: int,
                     rng: np.random.Generator) -> np.ndarray:
    """Assign elevation using fractal noise and a gaussian mask."""

    noise = PerlinNoise(seed=int(rng.integers(0, 10000)))
    center = np.array([width / 2.0, height / 2.0])
    sigma = min(width, height) / 3.0

    elev = np.zeros(len(cells))
    for i, poly in enumerate(cells):
        c = np.array(poly.centroid.coords[0])
        n = _fractal_noise(noise, c[0] * 0.02, c[1] * 0.02)
        base = (n + 1.0) / 2.0
        d = np.linalg.norm(c - center)
        g = np.exp(-(d ** 2) / (2 * sigma ** 2))
        elev[i] = base * g

    # Set boundary cells to sea level
    for i, poly in enumerate(cells):
        minx, miny, maxx, maxy = poly.bounds
        if minx <= 0 or miny <= 0 or maxx >= width or maxy >= height:
            elev[i] = 0.0

    # Redistribute elevations so that 50% of cells are below 0.5
    order = np.argsort(elev)
    ranks = np.empty(len(elev))
    ranks[order] = np.linspace(0.0, 1.0, len(elev))
    return ranks

