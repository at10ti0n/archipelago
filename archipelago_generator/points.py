"""Point generation utilities."""

from __future__ import annotations

from typing import Tuple

import numpy as np


def poisson_disk_sampling(width: int, height: int, radius: float, rng: np.random.Generator) -> np.ndarray:
    """Generate points using simple Poisson disk sampling."""
    cell_size = radius / np.sqrt(2)
    grid_width = int(np.ceil(width / cell_size))
    grid_height = int(np.ceil(height / cell_size))
    grid = -np.ones((grid_height, grid_width), dtype=int)

    points = []
    active = []

    def add_point(p: Tuple[float, float]):
        points.append(p)
        idx = len(points) - 1
        gx = int(p[0] / cell_size)
        gy = int(p[1] / cell_size)
        grid[gy, gx] = idx
        active.append(idx)

    add_point((rng.uniform(0, width), rng.uniform(0, height)))

    while active:
        idx = active[rng.integers(0, len(active))]
        base = points[idx]
        found = False
        for _ in range(30):
            ang = rng.uniform(0, 2 * np.pi)
            r = rng.uniform(radius, 2 * radius)
            x = base[0] + np.cos(ang) * r
            y = base[1] + np.sin(ang) * r
            if not (0 <= x < width and 0 <= y < height):
                continue
            gx = int(x / cell_size)
            gy = int(y / cell_size)
            xmin = max(gx - 2, 0)
            xmax = min(gx + 3, grid_width)
            ymin = max(gy - 2, 0)
            ymax = min(gy + 3, grid_height)
            too_close = False
            for yy in range(ymin, ymax):
                for xx in range(xmin, xmax):
                    pid = grid[yy, xx]
                    if pid >= 0:
                        px, py = points[pid]
                        if (px - x) ** 2 + (py - y) ** 2 < radius ** 2:
                            too_close = True
                            break
                if too_close:
                    break
            if not too_close:
                add_point((x, y))
                found = True
                break
        if not found:
            active.remove(idx)
    return np.array(points)


def lloyd_relaxation(points: np.ndarray, width: int, height: int, iterations: int) -> np.ndarray:
    """Apply Lloyd relaxation to points."""
    from scipy.spatial import Voronoi

    pts = points.copy()
    for _ in range(iterations):
        vor = Voronoi(pts)
        new_pts = []
        for i in range(len(pts)):
            region_index = vor.point_region[i]
            region = vor.regions[region_index]
            if -1 in region or len(region) == 0:
                new_pts.append(pts[i])
                continue
            verts = vor.vertices[region]
            cx = np.mean(np.clip(verts[:, 0], 0, width))
            cy = np.mean(np.clip(verts[:, 1], 0, height))
            new_pts.append((cx, cy))
        pts = np.array(new_pts)
    return pts

