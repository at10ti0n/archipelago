"""Biome classification."""

from __future__ import annotations

import numpy as np

# Available biome names including ocean water cells. Land biomes follow a
# simplified Whittaker diagram based on temperature and moisture.
BIOMES = [
    "ocean",
    "desert",
    "grassland",
    "forest",
    "dark_forest",
    "jungle",
    "snow",
    "tundra",
    "scorched",
]


def classify_biomes(land_mask: np.ndarray, temp: np.ndarray, moisture: np.ndarray) -> np.ndarray:
    """Classify biome for each cell using a coarse Whittaker diagram."""
    biome = np.empty(len(land_mask), dtype=object)
    for i in range(len(biome)):
        if not land_mask[i]:
            biome[i] = "ocean"
            continue

        t = temp[i]
        m = moisture[i]

        # extremely dry region independent of temperature
        if m < 0.05:
            biome[i] = "scorched"
            continue

        if t < 0.2:  # very cold
            biome[i] = "snow" if m > 0.5 else "tundra"
        elif t < 0.4:  # cold/temperate
            if m < 0.25:
                biome[i] = "desert"
            elif m < 0.5:
                biome[i] = "grassland"
            else:
                biome[i] = "forest"
        elif t < 0.7:  # temperate/warm
            if m < 0.25:
                biome[i] = "desert"
            elif m < 0.5:
                biome[i] = "grassland"
            elif m < 0.75:
                biome[i] = "forest"
            else:
                biome[i] = "dark_forest"
        else:  # hot
            if m < 0.3:
                biome[i] = "desert" if m > 0.05 else "scorched"
            elif m < 0.6:
                biome[i] = "grassland"
            else:
                biome[i] = "jungle"
    return biome

