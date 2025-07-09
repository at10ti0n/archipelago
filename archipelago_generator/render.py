"""Rendering utilities for archipelago results."""

from __future__ import annotations

from blessed import Terminal
import numpy as np

from .generator import Archipelago
from .rasterizer import rasterize

# Simple glyph and color mapping for biomes
BIOME_GLYPHS = {
    "ocean": ("~", (0, 0, 200)),
    "desert": (".", (200, 180, 50)),
    "grassland": (",", (50, 180, 50)),
    "forest": ("^", (20, 140, 20)),
    "dark_forest": ("^", (10, 100, 10)),
    "jungle": ("&", (0, 150, 0)),
    "snow": ("*", (240, 240, 240)),
    "tundra": ("'", (200, 200, 210)),
    "scorched": ("x", (120, 40, 0)),
}


def render_archipelago(arch: Archipelago) -> None:
    """Render the archipelago to the terminal using ASCII art."""
    grid = rasterize(arch.cells, arch.biome, arch.width, arch.height)
    term = Terminal()
    lines: list[str] = []
    for y in range(arch.height):
        line = ""
        for x in range(arch.width):
            biome = grid[y, x]
            glyph, rgb = BIOME_GLYPHS.get(biome, ("?", (255, 255, 255)))
            line += term.color_rgb(*rgb) + glyph + term.normal
        lines.append(line)
    print(term.home + "\n".join(lines))
