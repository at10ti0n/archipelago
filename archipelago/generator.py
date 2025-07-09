from __future__ import annotations

import numpy as np
from perlin_noise import PerlinNoise


def lloyd_relaxation(width: int, height: int, num_seeds: int, iterations: int, rng: np.random.Generator) -> np.ndarray:
    """Generate province seeds using Lloyd's relaxation."""
    seeds = np.column_stack([
        rng.integers(0, width, num_seeds),
        rng.integers(0, height, num_seeds),
    ])
    for _ in range(iterations):
        province_map = np.zeros((height, width), dtype=int)
        cell_points = [[] for _ in range(num_seeds)]
        for y in range(height):
            for x in range(width):
                dists = np.sum((seeds - np.array([x, y])) ** 2, axis=1)
                p = int(np.argmin(dists))
                province_map[y, x] = p
                cell_points[p].append((x, y))
        for i in range(num_seeds):
            if cell_points[i]:
                arr = np.array(cell_points[i])
                seeds[i, 0] = int(np.mean(arr[:, 0]))
                seeds[i, 1] = int(np.mean(arr[:, 1]))
    return seeds


def assign_provinces(width: int, height: int, seeds: np.ndarray) -> np.ndarray:
    """Assign each tile to the nearest seed."""
    province_map = np.zeros((height, width), dtype=int)
    for y in range(height):
        for x in range(width):
            dists = np.sum((seeds - np.array([x, y])) ** 2, axis=1)
            province_map[y, x] = int(np.argmin(dists))
    return province_map


def mark_borders(province_map: np.ndarray) -> np.ndarray:
    """Mark map borders where neighboring province differs."""
    height, width = province_map.shape
    border_map = np.zeros_like(province_map, dtype=bool)
    for y in range(height):
        for x in range(width):
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx < width and province_map[ny, nx] != province_map[y, x]:
                    border_map[y, x] = True
    return border_map


def _perlin(noise: PerlinNoise, width: int, height: int) -> np.ndarray:
    return np.array([[noise([x / width, y / height]) for x in range(width)] for y in range(height)])


def generate_elevation(width: int, height: int, rng: np.random.Generator) -> np.ndarray:
    base_noise = PerlinNoise(octaves=4, seed=int(rng.integers(0, 1e9)))
    ridge_noise = PerlinNoise(octaves=6, seed=int(rng.integers(0, 1e9)))
    elevation = _perlin(base_noise, width, height)
    ridges = np.abs(_perlin(ridge_noise, width, height))
    elev = (elevation * 0.7 + ridges * 0.3 + 1) / 2  # normalize to 0..1
    return elev


def smooth_coasts(elevation: np.ndarray, iterations: int = 1) -> np.ndarray:
    height, width = elevation.shape
    elev = elevation.copy()
    for _ in range(iterations):
        new = elev.copy()
        for y in range(height):
            for x in range(width):
                if elev[y, x] < 0.3:
                    vals = []
                    for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                        ny, nx = y+dy, x+dx
                        if 0<=ny<height and 0<=nx<width:
                            vals.append(elev[ny, nx])
                    if vals:
                        new[y, x] = (elev[y, x] + np.mean(vals)) / 2
        elev = new
    return elev


def generate_rainfall(width: int, height: int, elevation: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    rain_noise = PerlinNoise(octaves=4, seed=int(rng.integers(0, 1e9)))
    rainfall = (_perlin(rain_noise, width, height) + 1) / 2
    # simple rain shadow: reduce rainfall east of high mountains
    for y in range(height):
        moisture = 0.0
        for x in range(width):
            moisture = max(moisture * 0.9, rainfall[y, x])
            if elevation[y, x] > 0.6:
                moisture *= 0.5
            rainfall[y, x] = moisture
    rainfall = (rainfall - rainfall.min()) / (rainfall.max() - rainfall.min())
    return rainfall


def compute_temperature(elevation: np.ndarray) -> np.ndarray:
    height, width = elevation.shape
    lat = np.tile(np.linspace(1.0, 0.0, height)[:, None], (1, width))
    temp = lat - elevation * 0.5
    temp = (temp - temp.min()) / (temp.max() - temp.min())
    return temp


def compute_water_flux(elevation: np.ndarray):
    height, width = elevation.shape
    downslope = np.full((height, width, 2), -1, dtype=int)
    for y in range(height):
        for x in range(width):
            min_elev = elevation[y, x]
            best = None
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                ny, nx = y+dy, x+dx
                if 0<=ny<height and 0<=nx<width and elevation[ny, nx] < min_elev:
                    min_elev = elevation[ny, nx]
                    best = (ny, nx)
            if best:
                downslope[y, x] = best
    water_flux = np.ones((height, width))
    order = [(y,x) for y in range(height) for x in range(width)]
    order.sort(key=lambda p: -elevation[p])
    for y, x in order:
        ny, nx = downslope[y, x]
        if ny >= 0:
            water_flux[ny, nx] += water_flux[y, x]
    return water_flux, downslope


def trace_rivers(water_flux: np.ndarray, downslope: np.ndarray, elevation: np.ndarray, min_flux: float = 20.0):
    height, width = elevation.shape
    river_map = np.zeros((height, width), dtype=int)
    river_width = np.zeros((height, width), dtype=int)
    river_id = 1
    visited = set()
    coords = [(y, x) for y in range(height) for x in range(width) if water_flux[y, x] >= min_flux]
    coords.sort(key=lambda p: water_flux[p], reverse=True)
    for y, x in coords:
        if (y, x) not in visited:
            cy, cx = y, x
            while elevation[cy, cx] >= 0.26:
                if (cy, cx) in visited:
                    break
                visited.add((cy, cx))
                river_map[cy, cx] = river_id
                river_width[cy, cx] = int(max(1, np.log2(water_flux[cy, cx])))
                ny, nx = downslope[cy, cx]
                if ny < 0 or elevation[ny, nx] < 0.26:
                    break
                cy, cx = ny, nx
            river_id += 1
    return river_map, river_width


def place_cities(province_map: np.ndarray, river_map: np.ndarray, elevation: np.ndarray, n_cities: int = 1, min_dist: int = 10):
    height, width = elevation.shape
    city_coords = []
    for province_id in np.unique(province_map):
        candidates = []
        for y in range(height):
            for x in range(width):
                if province_map[y, x] == province_id and 0.26 < elevation[y, x] < 0.8:
                    if river_map[y, x] > 0 or any(
                        elevation[ny, nx] < 0.26
                        for dy in [-1, 0, 1]
                        for dx in [-1, 0, 1]
                        if 0 <= y + dy < height and 0 <= x + dx < width
                        for ny, nx in [(y + dy, x + dx)]
                    ):
                        candidates.append((y, x))
        if candidates:
            best = max(
                candidates,
                key=lambda c: min([np.hypot(c[0] - y, c[1] - x) for y, x in city_coords] or [1e9]),
            )
            city_coords.append(best)
    return city_coords


BIOME_GLYPHS = {
    "ocean": ("~", (0, 0, 200)),
    "plain": (".", (50, 200, 50)),
    "mountain": ("^", (180, 180, 180)),
    "snow": ("*", (220, 220, 220)),
}


def assign_biomes(elevation: np.ndarray, rainfall: np.ndarray, temperature: np.ndarray) -> np.ndarray:
    height, width = elevation.shape
    biome = np.empty((height, width), dtype=object)
    for y in range(height):
        for x in range(width):
            e = elevation[y, x]
            r = rainfall[y, x]
            t = temperature[y, x]
            if e < 0.26:
                biome[y, x] = "ocean"
            elif e > 0.8:
                biome[y, x] = "mountain" if t > 0.3 else "snow"
            else:
                biome[y, x] = "plain"
    return biome


def generate_world(width: int = 80, height: int = 40, seed: int = 0, num_provinces: int = 5):
    rng = np.random.default_rng(seed)
    seeds = lloyd_relaxation(width, height, num_provinces, 3, rng)
    provinces = assign_provinces(width, height, seeds)
    borders = mark_borders(provinces)
    elevation = generate_elevation(width, height, rng)
    elevation = smooth_coasts(elevation, iterations=2)
    rainfall = generate_rainfall(width, height, elevation, rng)
    temperature = compute_temperature(elevation)
    flux, downslope = compute_water_flux(elevation)
    river_map, river_width = trace_rivers(flux, downslope, elevation)
    cities = place_cities(provinces, river_map, elevation)
    biome = assign_biomes(elevation, rainfall, temperature)
    return {
        "provinces": provinces,
        "borders": borders,
        "elevation": elevation,
        "rainfall": rainfall,
        "temperature": temperature,
        "water_flux": flux,
        "river_map": river_map,
        "river_width": river_width,
        "cities": cities,
        "biome": biome,
    }
