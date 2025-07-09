"""Voronoi diagram utilities."""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
from shapely.geometry import Polygon, box, MultiPoint
from shapely.ops import voronoi_diagram
from scipy.spatial import Voronoi


def compute_voronoi(points: np.ndarray, width: int, height: int) -> List[Polygon]:
    """Compute bounded Voronoi cells as shapely polygons."""
    # Use scipy Voronoi then clip to bounding box
    bbox = box(0, 0, width, height)
    vor = Voronoi(points)
    regions = []
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
    return regions

