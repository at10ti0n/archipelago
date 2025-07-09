"""Climate simulation utilities."""

from __future__ import annotations

import numpy as np


def compute_temperature(cells, height: float) -> np.ndarray:
    temp = np.zeros(len(cells))
    for i, poly in enumerate(cells):
        y = poly.centroid.y / height
        temp[i] = 1 - y  # north colder
    return temp


def compute_rainfall(cells, rng: np.random.Generator) -> np.ndarray:
    from noise import pnoise2
    rain = np.zeros(len(cells))
    for i, poly in enumerate(cells):
        c = poly.centroid
        n = pnoise2(c.x * 0.01, c.y * 0.01, repeatx=1024, repeaty=1024, base=int(rng.integers(0, 10000)))
        rain[i] = (n + 1) / 2
    return rain

