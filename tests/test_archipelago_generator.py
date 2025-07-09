import numpy as np
from archipelago_generator import generate_archipelago


def test_deterministic():
    a1 = generate_archipelago(width=100, height=100, seed=1)
    a2 = generate_archipelago(width=100, height=100, seed=1)
    assert np.array_equal(a1.land, a2.land)
    assert np.array_equal(a1.elevation, a2.elevation)
    assert np.array_equal(a1.biome, a2.biome)


def test_cell_count():
    arch = generate_archipelago(width=100, height=100, seed=2)
    assert len(arch.cells) > 0
    assert arch.land.shape[0] == len(arch.cells)
