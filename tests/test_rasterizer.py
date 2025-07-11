import numpy as np

from archipelago_generator.rasterizer import Rasterizer


def test_rasterize_line():
    r = Rasterizer(10, 5, seed=1)
    line = [(0, 2), (9, 2)]
    mask = r.rasterize_polyline(line, brush_radius=0.5, sampling_density=1.0)
    assert mask.shape == (5, 10)
    assert mask[2].all()


def test_jitter_determinism():
    r1 = Rasterizer(10, 10, seed=42)
    r2 = Rasterizer(10, 10, seed=42)
    line = [(0.0, 0.0), (5.0, 5.0), (9.0, 9.0)]
    j1 = r1.jitter_polyline(line, freq=1.0, strength=1.0)
    j2 = r2.jitter_polyline(line, freq=1.0, strength=1.0)
    assert np.allclose(j1, j2)

