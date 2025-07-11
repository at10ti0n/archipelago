"""Archipelago generation orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from shapely.geometry import Polygon, LineString

from .points import poisson_disk_sampling, lloyd_relaxation, random_points
from .voronoi import compute_voronoi
from .elevation import assign_elevation
from .climate import compute_temperature, compute_rainfall
from .moisture import compute_moisture
from .biomes import classify_biomes
from .rivers import compute_rivers, place_cities, build_roads
from .borders import unite_regions, compute_borders
from .rasterizer import rasterize
from .utils import seeded_rng


@dataclass
class ArchipelagoParams:
    width: int = 200
    height: int = 200
    seed: Optional[int] = None
    point_count: int = 1024
    relax_iterations: int = 2
    sea_level: float = 0.5
    num_cities: int = 3


@dataclass
class Archipelago:
    width: int
    height: int
    cells: list[Polygon]
    land: np.ndarray
    elevation: np.ndarray
    temperature: np.ndarray
    rainfall: np.ndarray
    moisture: np.ndarray
    biome: np.ndarray
    river_map: np.ndarray
    river_width: np.ndarray
    road_map: np.ndarray
    cities: list[tuple[int, int]]
    borders: list[LineString]
    regions: np.ndarray


def generate_archipelago(**kwargs) -> Archipelago:
    params = ArchipelagoParams(**kwargs)
    rng = seeded_rng(params.seed)

    pts = random_points(params.point_count, params.width, params.height, rng)
    pts = lloyd_relaxation(pts, params.width, params.height, params.relax_iterations)
    cells, neighbors = compute_voronoi(pts, params.width, params.height)

    elevation = assign_elevation(cells, params.width, params.height, rng)
    land_mask = elevation > params.sea_level
    land = land_mask.astype(bool)
    temperature = compute_temperature(cells, params.height, rng)
    rainfall = compute_rainfall(cells, rng)
    moisture = compute_moisture(rainfall)
    biome = classify_biomes(land, temperature, moisture)

    regions = unite_regions(biome, neighbors)
    borders = compute_borders(cells, biome, neighbors, seed=int(rng.integers(0, 1_000_000)))

    # Rasterize elevation for river and city generation
    elev_grid = rasterize(cells, elevation, params.width, params.height)
    river_map, river_width = compute_rivers(elev_grid, sea_level=params.sea_level)
    cities = place_cities(
        river_map,
        elev_grid,
        n_cities=params.num_cities,
        sea_level=params.sea_level,
        rng=rng,
    )
    road_map = build_roads(
        cities,
        elev_grid,
        sea_level=params.sea_level,
        seed=int(rng.integers(0, 1_000_000)),
    )

    return Archipelago(
        width=params.width,
        height=params.height,
        cells=cells,
        land=land,
        elevation=elevation,
        temperature=temperature,
        rainfall=rainfall,
        moisture=moisture,
        biome=biome,
        river_map=river_map,
        river_width=river_width,
        road_map=road_map,
        cities=cities,
        borders=borders,
        regions=regions,
    )

