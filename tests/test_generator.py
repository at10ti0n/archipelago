import numpy as np
from archipelago.generator import generate_world

def test_deterministic():
    world1 = generate_world(width=20, height=10, seed=42, num_provinces=3)
    world2 = generate_world(width=20, height=10, seed=42, num_provinces=3)
    for key in ["provinces", "borders", "river_map", "biome"]:
        assert np.array_equal(world1[key], world2[key])
    assert world1["cities"] == world2["cities"]


def test_shapes():
    w = generate_world(width=20, height=10, seed=1, num_provinces=4)
    h, wdt = w["elevation"].shape
    assert h == 10 and wdt == 20
    assert w["provinces"].shape == (10, 20)
    assert w["river_width"].shape == (10, 20)
