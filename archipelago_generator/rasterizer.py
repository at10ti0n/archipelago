"""Rasterization utilities."""

from __future__ import annotations

from typing import List

import numpy as np
from shapely.geometry import Polygon, Point
from shapely.strtree import STRtree
from shapely.prepared import prep


def rasterize(cells: List[Polygon], values: np.ndarray, width: int, height: int) -> np.ndarray:
    """Rasterize polygon values to a regular grid using ``STRtree`` for speed."""

    grid = np.zeros((height, width), dtype=values.dtype)
    tree = STRtree(cells)
    index_map = {geom.wkb: idx for idx, geom in enumerate(cells)}
    prepared = [prep(c) for c in cells]

    for y in range(height):
        for x in range(width):
            pt_geom = Point(x + 0.5, y + 0.5)
            candidates = tree.query(pt_geom, predicate="contains")
            for geom in candidates:
                idx = index_map.get(geom.wkb)
                if idx is None:
                    continue
                if prepared[idx].contains(pt_geom):
                    grid[y, x] = values[idx]
                    break
    return grid

