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
from .rivers import compute_rivers
from .cities import place_cities
from .roads import build_roads
from .borders import unite_regions, compute_borders
from .rasterizer import rasterize, Rasterizer
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
    river_width_tiles: int = 1
    road_width_tiles: int = 1
    jitter: bool = False


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
    river_lines: list[list[tuple[float, float]]]
    road_map: np.ndarray
    road_lines: list[list[tuple[float, float]]]
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
    river_map, river_width, river_lines = compute_rivers(
        elev_grid, sea_level=params.sea_level
    )
    rasterizer = Rasterizer(params.width, params.height, seed=int(rng.integers(0, 1_000_000)))
    river_jitter = {'freq': 0.1, 'strength': 0.5} if params.jitter else None
    river_map = rasterizer.rasterize_rivers(
        river_lines,
        width_tiles=params.river_width_tiles,
        density=1.0,
        jitter=river_jitter,
    )
    cities = place_cities(
        river_map,
        elev_grid,
        n_cities=params.num_cities,
        sea_level=params.sea_level,
        rng=rng,
    )
    road_map, road_lines = build_roads(
        cities,
        elev_grid,
        sea_level=params.sea_level,
        seed=int(rng.integers(0, 1_000_000)),
    )
    road_jitter = {'freq': 0.2, 'strength': 0.3} if params.jitter else None
    road_map = rasterizer.rasterize_roads(
        road_lines,
        width_tiles=params.road_width_tiles,
        density=1.0,
        jitter=road_jitter,
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
        river_lines=river_lines,
        road_map=road_map,
        road_lines=road_lines,
        cities=cities,
        borders=borders,
        regions=regions,
    )

