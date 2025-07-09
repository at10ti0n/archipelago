"""Rasterization utilities."""

from __future__ import annotations

from typing import List

import numpy as np
from shapely.geometry import Polygon, Point


def rasterize(cells: List[Polygon], values: np.ndarray, width: int, height: int) -> np.ndarray:
    grid = np.zeros((height, width), dtype=values.dtype)
    for y in range(height):
        for x in range(width):
            pt = (x + 0.5, y + 0.5)
            for i, poly in enumerate(cells):
                if poly.contains(Point(pt)):
                    grid[y, x] = values[i]
                    break
    return grid

