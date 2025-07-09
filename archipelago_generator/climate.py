"""Climate simulation utilities."""

from __future__ import annotations

import numpy as np
from perlin_noise import PerlinNoise


def compute_temperature(cells, height: float) -> np.ndarray:
    temp = np.zeros(len(cells))
    for i, poly in enumerate(cells):
        y = poly.centroid.y / height
        temp[i] = 1 - y  # north colder
    return temp


def compute_rainfall(cells, rng: np.random.Generator) -> np.ndarray:
    rain = np.zeros(len(cells))
    for i, poly in enumerate(cells):
        c = poly.centroid
        seed = int(rng.integers(0, 10000))
        noise = PerlinNoise(seed=seed)
        n = noise([c.x * 0.01, c.y * 0.01])
        rain[i] = (n + 1) / 2
    return rain

