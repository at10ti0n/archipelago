"""Archipelago generation orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from shapely.geometry import Polygon

from .points import poisson_disk_sampling, lloyd_relaxation
from .voronoi import compute_voronoi
from .island_mask import generate_islands, classify_land
from .elevation import assign_elevation
from .climate import compute_temperature, compute_rainfall
from .moisture import compute_moisture
from .biomes import classify_biomes
from .utils import seeded_rng


@dataclass
class ArchipelagoParams:
    width: int = 200
    height: int = 200
    seed: Optional[int] = None
    point_radius: float = 20.0
    relax_iterations: int = 1
    num_islands: int = 3
    min_island_radius: float = 60.0
    max_island_radius: float = 100.0
    sea_level: float = 0.3


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


def generate_archipelago(**kwargs) -> Archipelago:
    params = ArchipelagoParams(**kwargs)
    rng = seeded_rng(params.seed)

    pts = poisson_disk_sampling(params.width, params.height, params.point_radius, rng)
    pts = lloyd_relaxation(pts, params.width, params.height, params.relax_iterations)
    cells = compute_voronoi(pts, params.width, params.height)

    islands = generate_islands(params.num_islands, params.width, params.height, rng,
                               params.min_island_radius, params.max_island_radius)
    land_mask = classify_land(cells, islands, params.sea_level, rng)
    land = np.array(land_mask, dtype=bool)

    elevation = assign_elevation(cells, land_mask, rng)
    temperature = compute_temperature(cells, params.height)
    rainfall = compute_rainfall(cells, rng)
    moisture = compute_moisture(rainfall)
    biome = classify_biomes(land, temperature, moisture)

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
    )

