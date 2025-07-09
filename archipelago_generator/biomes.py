"""Biome classification."""

from __future__ import annotations

import numpy as np

BIOMES = [
    "ocean",
    "desert",
    "grassland",
    "forest",
    "tundra",
]


def classify_biomes(land_mask: np.ndarray, temp: np.ndarray, moisture: np.ndarray) -> np.ndarray:
    biome = np.empty(len(land_mask), dtype=object)
    for i in range(len(biome)):
        if not land_mask[i]:
            biome[i] = "ocean"
            continue
        if temp[i] < 0.3:
            biome[i] = "tundra"
        elif moisture[i] < 0.3:
            biome[i] = "desert"
        elif moisture[i] < 0.6:
            biome[i] = "grassland"
        else:
            biome[i] = "forest"
    return biome

