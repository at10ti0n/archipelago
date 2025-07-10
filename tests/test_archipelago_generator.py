import numpy as np
from archipelago_generator import generate_archipelago
from archipelago_generator import render_archipelago
from archipelago_generator.rasterizer import rasterize
from archipelago_generator.rivers import SEA_LEVEL


def test_deterministic():
    a1 = generate_archipelago(width=100, height=100, seed=1)
    a2 = generate_archipelago(width=100, height=100, seed=1)
    assert np.array_equal(a1.land, a2.land)
    assert np.array_equal(a1.elevation, a2.elevation)
    assert np.array_equal(a1.biome, a2.biome)
    assert np.array_equal(a1.river_map, a2.river_map)
    assert np.array_equal(a1.road_map, a2.road_map)
    assert a1.cities == a2.cities


def test_cell_count():
    arch = generate_archipelago(width=100, height=100, seed=2)
    assert len(arch.cells) > 0
    assert arch.land.shape[0] == len(arch.cells)
    assert arch.river_map.shape == (arch.height, arch.width)
    assert arch.road_map.shape == (arch.height, arch.width)
    assert isinstance(arch.cities, list)


def test_render_runs(capsys):
    arch = generate_archipelago(width=30, height=30, seed=3)
    render_archipelago(arch)
    captured = capsys.readouterr()
    assert "\n" in captured.out


def test_render_legend(capsys):
    arch = generate_archipelago(width=30, height=30, seed=5)
    render_archipelago(arch, show_legend=True)
    captured = capsys.readouterr()
    output = captured.out
    assert "ocean" in output
    assert "city" in output
    assert "road" in output
    assert "river" in output


def test_roads_on_land():
    arch = generate_archipelago(width=60, height=60, seed=4)
    elev_grid = rasterize(arch.cells, arch.elevation, arch.width, arch.height)
    for y in range(arch.height):
        for x in range(arch.width):
            if arch.road_map[y, x]:
                assert elev_grid[y, x] >= SEA_LEVEL
