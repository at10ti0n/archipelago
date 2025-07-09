"""Elevation generation and simple erosion."""

from __future__ import annotations

from typing import List

import numpy as np
from noise import pnoise2
from shapely.geometry import Polygon


def assign_elevation(cells: List[Polygon], land_mask: List[bool], rng: np.random.Generator) -> np.ndarray:
    """Assign elevation based on distance to coast and noise."""
    elev = np.zeros(len(cells))
    for i, poly in enumerate(cells):
        centroid = poly.centroid
        noise = pnoise2(centroid.x * 0.02, centroid.y * 0.02, repeatx=1024, repeaty=1024, base=int(rng.integers(0, 10000)))
        base = (noise + 1) / 2
        elev[i] = base if land_mask[i] else 0.0
    return elev

