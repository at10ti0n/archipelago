"""Voronoi diagram utilities."""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
from shapely.geometry import Polygon, box, MultiPoint
from shapely.ops import voronoi_diagram
from scipy.spatial import Voronoi


def compute_voronoi(points: np.ndarray, width: int, height: int) -> Tuple[List[Polygon], List[set[int]]]:
    """Compute bounded Voronoi cells and adjacency."""
    # Use scipy Voronoi then clip to bounding box
    bbox = box(0, 0, width, height)
    vor = Voronoi(points)
    regions: List[Polygon] = []
    adjacency: List[set[int]] = [set() for _ in range(len(points))]
    for i, point in enumerate(points):
        region_index = vor.point_region[i]
        region = vor.regions[region_index]
        if -1 in region or len(region) == 0:
            # Use generic approach: compute Voronoi diagram via shapely
            break
        polygon = Polygon(vor.vertices[region])
        regions.append(polygon.intersection(bbox))
    if len(regions) != len(points):
        # Fallback shapely voronoi for boundary points
        pts = MultiPoint([tuple(p) for p in points])
        cells = voronoi_diagram(pts, envelope=bbox, edges=False)
        regions = [poly.intersection(bbox) for poly in cells.geoms]

    for a, b in vor.ridge_points:
        adjacency[a].add(b)
        adjacency[b].add(a)

    return regions, adjacency

