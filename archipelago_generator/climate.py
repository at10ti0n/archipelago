"""Climate simulation utilities."""

from __future__ import annotations

import numpy as np
from perlin_noise import PerlinNoise


def compute_temperature(cells, height: float) -> np.ndarray:
    noise = PerlinNoise(seed=42)
    temp = np.zeros(len(cells))
    for i, poly in enumerate(cells):
        y = poly.centroid.y / height
        grad = 1 - y
        n = noise([0, y * 3]) * 0.1
        temp[i] = np.clip(grad + n, 0.0, 1.0)
    return temp


def compute_rainfall(cells, rng: np.random.Generator) -> np.ndarray:
    """Generate continuous rainfall using a shared noise field."""

    noise = PerlinNoise(seed=int(rng.integers(0, 10000)))
    rain = np.zeros(len(cells))
    for i, poly in enumerate(cells):
        c = poly.centroid
        n = noise([c.x * 0.01, c.y * 0.01])
        rain[i] = (n + 1) / 2
    return rain

