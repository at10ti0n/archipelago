"""City placement utilities for the archipelago generator."""

from __future__ import annotations

from typing import List, Tuple
import numpy as np

SEA_LEVEL = 0.26


def place_cities(
    river_map: np.ndarray,
    elevation: np.ndarray,
    *,
    n_cities: int = 3,
    min_dist: int = 10,
    sea_level: float = SEA_LEVEL,
    rng: np.random.Generator | None = None,
) -> List[Tuple[int, int]]:
    """Place cities near rivers or coasts with spacing."""

    height, width = elevation.shape
    candidates: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            if sea_level < elevation[y, x] < 0.8:
                if river_map[y, x] > 0 or any(
                    0 <= y + dy < height
                    and 0 <= x + dx < width
                    and elevation[y + dy, x + dx] < sea_level
                    for dy in [-1, 0, 1]
                    for dx in [-1, 0, 1]
                ):
                    candidates.append((y, x))

    if rng is None:
        rng = np.random.default_rng(0)
    rng.shuffle(candidates)
    cities: list[tuple[int, int]] = []
    for c in candidates:
        if all(np.hypot(c[0] - y, c[1] - x) >= min_dist for y, x in cities):
            cities.append(c)
        if len(cities) == n_cities:
            break
    return cities
