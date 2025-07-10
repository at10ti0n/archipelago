"""Border distortion and region merging utilities."""

from __future__ import annotations

from typing import List, Set

import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.geometry.base import BaseGeometry
from shapely.prepared import prep
from perlin_noise import PerlinNoise


def compute_adjacency(cells: List[Polygon]) -> List[Set[int]]:
    """Return adjacency list of polygons sharing an edge."""
    n = len(cells)
    neighbors: List[Set[int]] = [set() for _ in range(n)]
    prepared = [prep(c) for c in cells]
    bboxes = [c.bounds for c in cells]
    for i in range(n):
        minx1, miny1, maxx1, maxy1 = bboxes[i]
        for j in range(i + 1, n):
            minx2, miny2, maxx2, maxy2 = bboxes[j]
            if maxx1 < minx2 or maxx2 < minx1 or maxy1 < miny2 or maxy2 < miny1:
                continue
            if prepared[i].touches(cells[j]):
                inter = cells[i].intersection(cells[j])
                if isinstance(inter, BaseGeometry) and inter.geom_type in ("LineString", "MultiLineString") and not inter.is_empty:
                    neighbors[i].add(j)
                    neighbors[j].add(i)
    return neighbors


def unite_regions(biomes: np.ndarray, neighbors: List[Set[int]]) -> np.ndarray:
    """Flood fill adjacent cells of same biome and return region ids."""
    n = len(biomes)
    regions = -np.ones(n, dtype=int)
    cur = 0
    for i in range(n):
        if regions[i] != -1:
            continue
        queue = [i]
        regions[i] = cur
        while queue:
            u = queue.pop()
            for v in neighbors[u]:
                if regions[v] == -1 and biomes[v] == biomes[u]:
                    regions[v] = cur
                    queue.append(v)
        cur += 1
    return regions


def _distort_line(line: LineString, noise: PerlinNoise, *, amplitude: float, frequency: float) -> LineString:
    """Return a distorted copy of ``line`` using 1D noise."""
    if line.length == 0:
        return line
    (x1, y1), (x2, y2) = line.coords[0], line.coords[-1]
    vec = np.array([x2 - x1, y2 - y1])
    norm = np.array([-vec[1], vec[0]])
    if np.allclose(norm, 0):
        return line
    norm = norm / np.linalg.norm(norm)
    steps = max(int(line.length / 5), 2)
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = x1 + vec[0] * t
        y = y1 + vec[1] * t
        offset = noise(t * frequency) * amplitude
        pts.append((x + norm[0] * offset, y + norm[1] * offset))
    return LineString(pts)


def compute_borders(
    cells: List[Polygon],
    biomes: np.ndarray,
    neighbors: List[Set[int]],
    *,
    amplitude: float = 2.0,
    frequency: float = 0.1,
    seed: int = 0,
) -> List[LineString]:
    """Compute distorted borders between different biomes."""
    noise = PerlinNoise(seed=seed)
    lines: List[LineString] = []
    for i, neigh in enumerate(neighbors):
        for j in neigh:
            if j <= i:
                continue
            if biomes[i] == biomes[j]:
                continue
            inter = cells[i].intersection(cells[j])
            if inter.is_empty:
                continue
            if inter.geom_type == "LineString":
                lines.append(_distort_line(inter, noise, amplitude=amplitude, frequency=frequency))
            elif inter.geom_type == "MultiLineString":
                for geom in inter.geoms:
                    lines.append(_distort_line(geom, noise, amplitude=amplitude, frequency=frequency))
    return lines

