"""Rasterization utilities."""

from __future__ import annotations

from typing import List, Tuple, Optional, Dict

import numpy as np
from shapely.geometry import Polygon, Point
from shapely.strtree import STRtree
from shapely.prepared import prep
from perlin_noise import PerlinNoise


def rasterize(cells: List[Polygon], values: np.ndarray, width: int, height: int) -> np.ndarray:
    """Rasterize polygon values to a regular grid using ``STRtree`` for speed."""

    grid = np.zeros((height, width), dtype=values.dtype)
    tree = STRtree(cells)
    prepared = [prep(c) for c in cells]

    for y in range(height):
        for x in range(width):
            pt_geom = Point(x + 0.5, y + 0.5)
            candidate_idxs = tree.query(pt_geom, predicate="intersects")
            for idx in candidate_idxs:
                if prepared[idx].contains(pt_geom):
                    grid[y, x] = values[idx]
                    break
    return grid


class Rasterizer:
    """Utility to rasterize polylines into boolean masks."""

    def __init__(self, width: int, height: int, seed: int | None = None) -> None:
        self.width = width
        self.height = height
        self.noise = PerlinNoise(octaves=1, seed=seed or 0)

    def jitter_polyline(
        self,
        polyline: List[Tuple[float, float]],
        freq: float,
        strength: float,
    ) -> List[Tuple[float, float]]:
        """Displace vertices along the normal by Perlin noise."""

        if len(polyline) < 2:
            return polyline

        jit: List[Tuple[float, float]] = [polyline[0]]
        for i in range(1, len(polyline) - 1):
            x, y = polyline[i]
            x0, y0 = polyline[i - 1]
            x1, y1 = polyline[i + 1]
            dx = x1 - x0
            dy = y1 - y0
            nx, ny = -dy, dx
            norm = (nx ** 2 + ny ** 2) ** 0.5
            if norm != 0:
                nx /= norm
                ny /= norm
                u, v = x / freq, y / freq
                offset = (self.noise([u, v]) - 0.5) * 2 * strength
                x += nx * offset
                y += ny * offset
            jit.append((x, y))
        jit.append(polyline[-1])
        return jit

    def rasterize_polyline(
        self,
        polyline: List[Tuple[float, float]],
        brush_radius: float,
        sampling_density: float,
    ) -> np.ndarray:
        """Rasterize a single polyline to a boolean mask."""

        mask = np.zeros((self.height, self.width), dtype=bool)
        if len(polyline) < 2:
            return mask

        for p0, p1 in zip(polyline[:-1], polyline[1:]):
            x0, y0 = p0
            x1, y1 = p1
            seg_len = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            samples = max(int(np.ceil(seg_len * sampling_density)), 1)
            for i in range(samples + 1):
                t = i / samples
                x = x0 + (x1 - x0) * t
                y = y0 + (y1 - y0) * t
                xmin = int(max(0, np.floor(x - brush_radius)))
                xmax = int(min(self.width - 1, np.ceil(x + brush_radius)))
                ymin = int(max(0, np.floor(y - brush_radius)))
                ymax = int(min(self.height - 1, np.ceil(y + brush_radius)))
                for yy in range(ymin, ymax + 1):
                    for xx in range(xmin, xmax + 1):
                        if (xx - x) ** 2 + (yy - y) ** 2 <= brush_radius ** 2:
                            mask[yy, xx] = True
        return mask

    def _combine_masks(self, masks: List[np.ndarray]) -> np.ndarray:
        combined = np.zeros((self.height, self.width), dtype=bool)
        for m in masks:
            combined |= m
        return combined

    def rasterize_rivers(
        self,
        rivers: List[List[Tuple[float, float]]],
        width_tiles: int = 1,
        density: float = 1.0,
        jitter: Optional[Dict[str, float]] = None,
    ) -> np.ndarray:
        masks = []
        radius = max(0.5, width_tiles / 2)
        for line in rivers:
            if jitter:
                line = self.jitter_polyline(line, jitter.get("freq", 1.0), jitter.get("strength", 1.0))
            masks.append(self.rasterize_polyline(line, radius, density))
        return self._combine_masks(masks)

    def rasterize_roads(
        self,
        roads: List[List[Tuple[float, float]]],
        width_tiles: int = 1,
        density: float = 1.0,
        jitter: Optional[Dict[str, float]] = None,
    ) -> np.ndarray:
        masks = []
        radius = max(0.5, width_tiles / 2)
        for line in roads:
            if jitter:
                line = self.jitter_polyline(line, jitter.get("freq", 1.0), jitter.get("strength", 1.0))
            masks.append(self.rasterize_polyline(line, radius, density))
        return self._combine_masks(masks)


