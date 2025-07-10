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

# Additional glyphs for non-biome features
FEATURE_GLYPHS = {
    "city": ("@", (230, 180, 0)),
    "road": (":", (180, 100, 50)),
    "river": ("=", (80, 180, 255)),
    "wide river": ("≡", (0, 100, 255)),
}


def render_archipelago(arch: Archipelago, show_legend: bool = False) -> None:
    """Render the archipelago with cities, rivers and roads.

    Parameters
    ----------
    arch:
        The archipelago data object to render.
    show_legend:
        If ``True``, print a legend of biome glyphs below the map.
    """
    grid = rasterize(arch.cells, arch.biome, arch.width, arch.height)
    term = Terminal()
    lines: list[str] = []
    cities = set(arch.cities)
    for y in range(arch.height):
        line = ""
        for x in range(arch.width):
            ch: str
            rgb: tuple[int, int, int]
            if (y, x) in cities:
                ch, rgb = "@", (230, 180, 0)
            elif arch.road_map[y, x]:
                ch, rgb = ":", (180, 100, 50)
            elif arch.river_map[y, x] > 0:
                if arch.river_width[y, x] > 2:
                    ch, rgb = "≡", (0, 100, 255)
                else:
                    ch, rgb = "=", (80, 180, 255)
            else:
                biome = grid[y, x]
                ch, rgb = BIOME_GLYPHS.get(biome, ("?", (255, 255, 255)))
            line += term.color_rgb(*rgb) + ch + term.normal
        lines.append(line)
    print(term.home + "\n".join(lines))

    if show_legend:
        legend_lines = []
        for biome in sorted(BIOME_GLYPHS):
            glyph, rgb = BIOME_GLYPHS[biome]
            legend_lines.append(term.color_rgb(*rgb) + glyph + term.normal + f" {biome}")

        for feature in ["city", "road", "river", "wide river"]:
            glyph, rgb = FEATURE_GLYPHS[feature]
            legend_lines.append(term.color_rgb(*rgb) + glyph + term.normal + f" {feature}")

        print("\n".join(legend_lines))
