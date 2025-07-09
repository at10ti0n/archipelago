⸻

🌍 Vagabond-Style Procedural Overworld Mega PRD (with Lloyd’s Relaxation, Complete Steps)

⸻

1. Purpose

Produce organic, natural, and reproducible procedural fantasy overworld maps for games, with:
	•	Detailed and physically plausible geography (elevation, mountains, coasts, rivers)
	•	Province system with natural borders (Fortune’s/Voronoi, with Lloyd’s relaxation)
	•	Realistic river networks (water flux, accumulation, and width)
	•	Cities and roads, sensibly placed and connected
	•	Full-colored ASCII/CP437 rendering for terminal with blessed
	•	Configurable seed, map size, and province/city counts

⸻

2. Dependencies
	•	numpy
	•	perlin-noise
	•	scipy
	•	blessed

pip install numpy perlin-noise scipy blessed


⸻

3. Data Structures
	•	2D numpy arrays for: elevation, water, rainfall, temperature, province, borders, river ID/width, road, city, overlays.
	•	Province seeds/sites: (x, y) for each Voronoi cell (province center).
	•	List of cities (with their province).
	•	Map overlays: per-tile ASCII/CP437 glyph and RGB color.

⸻

4. Generation Pipeline

A. Generate Province Seeds with Lloyd’s Relaxation

Why: Random Voronoi seeds yield clumped cells; Lloyd’s algorithm ensures even, centroidal, more “natural” province shapes.
	1.	Generate N initial random province seed points.
	2.	For several iterations:
	•	Assign each map cell to nearest seed (Voronoi cell assignment).
	•	For each cell, compute centroid (average (x,y) of all map tiles assigned to that seed).
	•	Move each seed to its centroid.
	3.	Final seeds are the province centers.

Code:

def lloyd_relaxation(width, height, num_seeds, iterations, rng):
    # Step 1: Random initial seeds
    seeds = np.column_stack([
        rng.integers(0, width, num_seeds),
        rng.integers(0, height, num_seeds)
    ])
    for _ in range(iterations):
        province_map = np.zeros((height, width), dtype=int)
        cell_points = [[] for _ in range(num_seeds)]
        # Assign to nearest
        for y in range(height):
            for x in range(width):
                dists = np.sum((seeds - np.array([x, y]))**2, axis=1)
                p = np.argmin(dists)
                province_map[y, x] = p
                cell_points[p].append((x, y))
        # Move each seed to centroid
        for i in range(num_seeds):
            if cell_points[i]:
                arr = np.array(cell_points[i])
                seeds[i, 0] = int(np.mean(arr[:, 0]))
                seeds[i, 1] = int(np.mean(arr[:, 1]))
    return seeds

Call with e.g. lloyd_relaxation(width, height, num_seeds, 3, np.random.default_rng(seed)).

⸻

B. Assign Provinces & Borders
	1.	For each map tile, assign to nearest seed/site (after relaxation).
	2.	Borders = tiles adjacent to different province.

def assign_provinces(width, height, seeds):
    province_map = np.zeros((height, width), dtype=int)
    for y in range(height):
        for x in range(width):
            dists = np.sum((seeds - np.array([x, y]))**2, axis=1)
            province_map[y, x] = np.argmin(dists)
    return province_map

def mark_borders(province_map):
    height, width = province_map.shape
    border_map = np.zeros_like(province_map, dtype=bool)
    for y in range(height):
        for x in range(width):
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                ny, nx = y+dy, x+dx
                if 0<=ny<height and 0<=nx<width and province_map[ny, nx]!=province_map[y, x]:
                    border_map[y, x]=True
    return border_map


⸻

C. Elevation & Ridged Mountains
	•	Use Perlin noise for base elevation.
	•	Add an “absolute value” Perlin noise for ridged mountains.

⸻

D. Coast Smoothing
	•	After elevation is generated, iteratively smooth low-elevation (coast) tiles for natural coastlines.
	•	(Optional: For each sea tile, average with adjacent elevation to reduce noisy islets.)

⸻

E. Rainfall & Rain Shadow
	•	Generate Perlin noise for base rainfall.
	•	Apply rain shadow algorithm:
	•	For each row (assuming west-to-east wind), track moisture, reduce after crossing high mountains.
	•	Normalize.

⸻

F. Temperature
	•	Temperature = latitude effect (colder at poles) - elevation effect (colder up high)
	•	Normalize.

⸻

G. Water Flow / Flux Map for Rivers
	•	For each cell, count how many upstream cells drain through it (“water flux”).
	•	Use “downslope neighbor” for every tile (steepest neighbor).
	•	For each cell, recursively accumulate upstream cell counts.

def compute_water_flux(elevation):
    height, width = elevation.shape
    downslope = np.full((height, width, 2), -1, dtype=int)
    for y in range(height):
        for x in range(width):
            min_elev = elevation[y,x]
            best = None
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                ny, nx = y+dy, x+dx
                if 0<=ny<height and 0<=nx<width and elevation[ny,nx]<min_elev:
                    min_elev = elevation[ny, nx]
                    best = (ny, nx)
            if best:
                downslope[y, x] = best
    # Compute water flux
    water_flux = np.ones((height, width))
    order = [(y,x) for y in range(height) for x in range(width)]
    order.sort(key=lambda p: -elevation[p])  # high to low
    for y, x in order:
        ny, nx = downslope[y, x]
        if ny>=0:
            water_flux[ny, nx] += water_flux[y, x]
    return water_flux, downslope


⸻

H. River Placement and Width
	•	River sources: high water flux and high elevation (not too near sea)
	•	Each river follows downslope map to sea.
	•	As river flows, keep count of flux to set width.

def trace_rivers(water_flux, downslope, elevation, min_flux=20):
    height, width = elevation.shape
    river_map = np.zeros((height, width), dtype=int)
    river_width = np.zeros((height, width), dtype=int)
    river_id = 1
    visited = set()
    for y in range(height):
        for x in range(width):
            if water_flux[y, x] >= min_flux and (y, x) not in visited:
                path = []
                cy, cx = y, x
                while elevation[cy, cx] >= 0.26:
                    if (cy, cx) in visited:
                        break
                    visited.add((cy, cx))
                    path.append((cy, cx))
                    river_map[cy, cx] = river_id
                    river_width[cy, cx] = int(max(1, np.log2(water_flux[cy, cx])))
                    ncy, ncx = downslope[cy, cx]
                    if ncy<0 or elevation[ncy, ncx]<0.26:
                        break
                    cy, cx = ncy, ncx
                river_id += 1
    return river_map, river_width


⸻

I. Biome Assignment
	•	Use elevation, rainfall, and temperature to select biome (see above).

⸻

J. City Placement
	•	One “capital” per province (choose highest water flux tile on river/coast in province).
	•	Remaining cities: well-spaced, also on rivers/coasts if possible.

def place_cities(province_map, river_map, elevation, n_cities=1, min_dist=10):
    height, width = elevation.shape
    city_coords = []
    for province_id in np.unique(province_map):
        candidates = []
        for y in range(height):
            for x in range(width):
                if province_map[y, x]==province_id and elevation[y, x]>0.26 and elevation[y, x]<0.8:
                    if river_map[y, x]>0 or any(elevation[ny,nx]<0.26 for dy in [-1,0,1] for dx in [-1,0,1] 
                        if 0<=y+dy<height and 0<=x+dx<width for ny,nx in [(y+dy,x+dx)]):
                        candidates.append((y,x))
        # Pick city farthest from others (capital placement)
        if candidates:
            best = max(candidates, key=lambda c: min([np.hypot(c[0]-y, c[1]-x) for y,x in city_coords] or [1e9]))
            city_coords.append(best)
    return city_coords


⸻

K. Road Placement
	•	Use A* or Dijkstra to connect cities, cost = base+elevation*multiplier, prefer valleys, allow bridges.
	•	Record as a bool map.

⸻

L. Final Rendering
	•	Overlay province coloring, borders, rivers (variable width), cities, and roads atop ASCII biomes.
	•	Use blessed for full RGB in terminal.

⸻

5. Rendering Details
	•	Each overlay has distinct glyph and color priority:
	•	City: @, gold
	•	Thick river: ≡, blue
	•	Thin river: =, light blue
	•	Border: #, purple
	•	Road: :, brown
	•	Province fill: subtle background color (optional, not always visible in terminals)
	•	Biome: glyph/color as in table

⸻

6. Success Criteria
	•	Provinces have natural, evenly sized/centered shapes (thanks to Lloyd’s algorithm).
	•	Rivers grow wider with accumulation/tributaries and flow sensibly to sea.
	•	Cities are capitals per province, well distributed and mostly on rivers/coasts.
	•	Roads connect cities, prefer valleys, and avoid mountains when possible.
	•	Everything renders as colored ASCII in terminal, overlays don’t clash.
	•	Map is reproducible for any seed and config.

⸻

7. Extensibility
	•	Add province names and color fills.
	•	Place ports/farms around cities.
	•	Label rivers and provinces.
	•	Support multi-scale maps (zoom in/out).
	•	Export to PNG or JSON for game use.

⸻

8. Pipeline Summary for Implementation
	1.	Initialize RNG and settings (width, height, seed, n_provinces, n_cities)
	2.	Run Lloyd’s relaxation for province seeds
	3.	Assign province for each tile (Voronoi)
	4.	Mark province borders
	5.	Generate elevation and ridge maps, smooth coasts
	6.	Generate rainfall and apply rain shadow
	7.	Compute temperature from latitude and elevation
	8.	Compute downslope and water flux for each cell
	9.	Trace rivers along downslope, using flux for width
	10.	Assign biome for each tile
	11.	Place cities (one per province, spaced out)
	12.	Carve roads using A or similar*
	13.	Prepare overlays (city, river, road, border, province fill)
	14.	Render map using blessed, prioritizing overlays

⸻

9. References
	•	Vagabond Map Generation
	•	Vagabond Borders, Rivers, Cities, Roads
	•	Lloyd’s Algorithm

⸻
