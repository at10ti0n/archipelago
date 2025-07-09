Product Requirements Document (PRD)

Archipelago Procedural Map Generator

⸻

Table of Contents
1.Overview & Objectives
2.High-Level Architecture
3.Functional Requirements
•3.1 Point & Diagram Generation
•3.2 Island & Ocean Partitioning (Archipelago)
•3.3 Elevation & Erosion Simulation
•3.4 Climate Simulation
•3.5 Moisture & River/Lake Routing
•3.6 Biome & Vegetation Assignment
•3.7 Coastline & Polygon-to-Tile Conversion
4.Non-Functional Requirements
5.File Structure & Modules
6.Data Flow & Algorithmic Steps
7.Integration & Extensibility
8.Testing & Quality Assurance
9.Future Enhancements

⸻

1. Overview & Objectives

Purpose:
Create a standalone Archipelago Procedural Map Generator that produces rich, multi-island polygon maps using Amit Patel’s techniques for Voronoi-based map generation (http://www-cs-students.stanford.edu/~amitp/game-programming/polygon-map-generation/) and the enhancements demonstrated in the Vagabond approach (https://pvigier.github.io/2019/05/12/vagabond-map-generation.html).

Key Goals:
•Support multiple islands (archipelago) with configurable count, size, and clustering.
•Provide fully procedural generation: points→Voronoi→island mask→elevation→erosion→climate→rivers→biomes→vegetation→raster.
•Ensure seamless rivers, realistic erosion, seasonal climate, and ecologically plausible biomes.
•Offer both vector (polygon) export and tile/raster output for game integration.

⸻

2. High-Level Architecture

+----------------------------------------------+
|              ArchipelagoGenerator            |
|   (generator.py orchestrates all steps)      |
+------------+---------------------------------+
             |
             v
+------------+-------------+     +-----------+
|   points.py              |     | utils.py  |
|   Poisson disk & Lloyd   |     | noise,    |
+------------+-------------+     | interpolation
             |                   +------^----+
             v                          |
+------------+-------------+            |
|   voronoi.py             |            |
|   Fortune’s + relaxation  <------------+
+------------+-------------+
             |
             v
+------------+-------------+
|   island_mask.py         |
|   Archipelago clustering |
+------------+-------------+
             |
             v
+------------+-------------+     +-----------+
|   elevation.py           |     | erosion.py|
|   Distance + noise       |     | (hydraulic +
+------------+-------------+     |  thermal)  |
             |                   +-----^-----+
             v                         |
+------------+-------------+          |
|   climate.py             |          |
|   Temperature & wind     |          |
+------------+-------------+          |
             |                         |
             v                         |
+------------+-------------+          |
|   moisture.py            |          |
|   Rainfall & diffusion   |          |
+------------+-------------+          |
             |                         |
             v                         |
+------------+-------------+          |
|   rivers.py              |          |
|   River routing (graph)  |          |
+------------+-------------+          |
             |                         |
             v                         |
+------------+-------------+          |
|   biomes.py               |          |
|   Whittaker lookup        |          |
+------------+-------------+          |
             |                         |
             v                         |
+------------+-------------+          |
|   vegetation.py          |          |
|   Clusters (trees, cacti)|          |
+------------+-------------+          |
             |                         |
             v                         |
+------------+-------------+          |
|   rasterizer.py          |          |
|   Polygon→Tile/PNG       |          |
+--------------------------+-----------+


⸻

3. Functional Requirements

3.1 Point & Diagram Generation
•Parameters:
•width, height
•point_count or density
•relaxation_steps for Lloyd algorithm
•Behavior:
•Generate Poisson-disk sampled points.
•Build Voronoi diagram via Fortune’s algorithm.
•Apply Lloyd relaxation for uniform cell distribution.

3.2 Island & Ocean Partitioning (Archipelago)
•Parameters:
•num_islands, min_island_radius, max_island_radius
•clustering_factor (0–1)
•sea_level_threshold
•Behavior:
•Place num_islands center points randomly.
•For each Voronoi cell, compute mask = max over all island center falloffs:
mask_i = 1 - min(1,d(cell,center_i)/r_i)
•Combine with Perlin noise to shape islands.
•Classify cell as land if mask + noise > sea_level_threshold, else ocean.

3.3 Elevation & Erosion Simulation
•Elevation Assignment:
•Initial elevation = mask-driven coastal falloff + Perlin noise.
•Hydraulic Erosion:
•Simulate raindrop paths on the polygon mesh: erode at high slope, carry sediment, deposit downstream.
•Thermal Erosion:
•Apply talus angle smoothing on mesh edges: redistribute mass where slope > threshold.
•Post-Erosion Normalization:
•Recompute cell elevation as average of corner elevations.

3.4 Climate Simulation
•Temperature Map:
•Base latitudinal gradient + noise + seasonal sinusoidal shift.
•Wind Bands:
•Define Hadley (trade), Ferrel (westerlies), Polar cells by latitude bands.
•Rainfall Transport:
•Initialize moisture=1.0 at wind-upstream ocean edge.
•For each cell in wind order:
M_cell = M_upstream * e^{-k * E_cell} + evaporation
•Seasonal multipliers to simulate wet/dry seasons.

3.5 Moisture & River/Lake Routing
•Moisture Diffusion:
•Spread moisture graph-based from ocean and existing rivers.
•River Source Selection:
•Choose top N high-elevation, high-moisture land cells as river heads.
•Graph Routing:
•On dual graph, route each source downhill to nearest ocean cell.
•At local minima, form a lake polygon and continue river from lake spillover point.

3.6 Biome & Vegetation Assignment
•Whittaker Biome Matrix:
•Inputs: normalized Temperature (T) and Moisture (M) per cell.
•Lookup table assigns biome (e.g., rainforest, savanna, tundra, polar desert).
•Vegetation Decoration:
•Forest biomes: scatter tree clusters via noise threshold.
•Grassland: shrub patches.
•Desert: cacti or oasis near moisture maxima.

3.7 Coastline & Polygon-to-Tile Conversion
•Coastlines:
•Mark edges between land/ocean cells as coastline segments.
•Rasterization:
•Optionally rasterize polygons to a 2D tile grid at desired resolution.
•Assign each tile the biome/elevation/moisture of its containing polygon.
•Export:
•JSON of polygon graph with attributes.
•PNG image or ASCII tilemap.

⸻

4. Non-Functional Requirements
•Performance: Full map (5k cells) < 500 ms on desktop.
•Determinism: Seeded RNG for reproducibility.
•Modularity: Each step in its own module, clear interfaces.
•Dependencies:
•numpy, scipy (Voronoi), noise (Perlin), shapely (geometry ops), Pillow (raster).
•Documentation: Docstrings for every class/method; in-code comments for algorithms.
•Portability: Python 3.8+, minimal external binaries.

⸻

5. File Structure & Modules

archipelago_generator/
├── generator.py         # Orchestrates full pipeline
├── points.py            # Poisson-disk + Lloyd relaxation
├── voronoi.py           # Voronoi construction & cell graph
├── island_mask.py       # Multi-island mask & land/ocean classification
├── elevation.py         # Base elevation + erosion module
├── erosion.py           # Hydraulic & thermal erosion on mesh
├── climate.py           # Temperature & wind model
├── moisture.py          # Moisture transport & diffusion
├── rivers.py            # River & lake routing
├── biomes.py            # Biome lookup & vegetation scatter
├── rasterizer.py        # Polygon→tile/PNG export
├── utils.py             # Shared utilities (noise wrappers, helpers)
└── examples/
    └── demo.py          # Example usage & parameter presets

⸻

6. Data Flow & Algorithmic Steps
1.generate_archipelago(params) in generator.py.
2.Points → Voronoi:
•points.generate() → voronoi.compute() → cells, graph.
3.Island Mask:
•island_mask.classify(cells, params).
4.Elevation + Erosion:
•elevation.assign(cells) → erosion.simulate(mesh).
5.Climate:
•climate.compute_temperature(cells) → climate.compute_winds().
6.Moisture & Rivers:
•moisture.transport(cells, winds) → rivers.route(cells, graph).
7.Biomes & Vegetation:
•biomes.classify(cells, T, M) → vegetation.scatter(cells).
8.Rasterization/Export:
•rasterizer.to_tilemap(cells, resolution) & rasterizer.export_png().

⸻

7. Integration & Extensibility
•API:

from archipelago_generator import generate_archipelago
result = generate_archipelago(seed=42, num_islands=10, width=2000, height=2000, ...)

•Hooks:
•Expose intermediate data (polygon graph, elevation grid).
•Allow custom erosion, biome, or river rules via strategy pattern.

⸻

8. Testing & Quality Assurance
•Unit Tests: For each module (e.g. test_points.py, test_rivers.py).
•Property Tests:
•Rivers always descend.
•Island count matches num_islands parameter approximately.
•Benchmarks: Time each stage, ensure performance targets.

⸻

9. Future Enhancements
•Dynamic Seasons: Animate seasonal changes in moisture/biomes.
•Vegetation Growth: Simulate forest spread over time.
•3D Mesh Export: Generate terrain meshes for game engines.
•Interactive Editing: GUI to tweak island shapes, elevation curves.

⸻

This PRD provides a comprehensive blueprint for a next-generation Archipelago Map Generator, combining polygon-based map generation, realistic climate and erosion, and rich biome ecosystems.
