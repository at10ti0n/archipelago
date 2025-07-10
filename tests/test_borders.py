import numpy as np
from shapely.geometry import Polygon

from archipelago_generator.borders import compute_adjacency, unite_regions, compute_borders


def test_regions_and_borders():
    # two adjacent squares with different biomes
    cells = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
    ]
    biomes = np.array(["forest", "grassland"], dtype=object)
    neigh = compute_adjacency(cells)
    assert neigh[0] == {1} and neigh[1] == {0}

    regions = unite_regions(biomes, neigh)
    assert regions[0] != regions[1]

    lines = compute_borders(cells, biomes, neigh, amplitude=0.5, frequency=0.5, seed=1)
    assert len(lines) == 1
    assert not lines[0].equals(cells[0].intersection(cells[1]))
