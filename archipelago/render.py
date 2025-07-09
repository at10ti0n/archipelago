from __future__ import annotations

import numpy as np
from blessed import Terminal
from .generator import BIOME_GLYPHS


def render_map(world: dict):
    term = Terminal()
    elevation = world["elevation"]
    provinces = world["provinces"]
    borders = world["borders"]
    biome = world["biome"]
    river_map = world["river_map"]
    river_width = world["river_width"]
    cities = set(world["cities"])

    height, width = elevation.shape
    lines = []
    for y in range(height):
        line = ""
        for x in range(width):
            ch = " "
            color = term.white
            if (y, x) in cities:
                ch, rgb = "@", (230, 180, 0)
                color = term.color_rgb(*rgb)
            elif river_map[y, x] > 0:
                if river_width[y, x] > 2:
                    ch, rgb = "≡", (0, 100, 255)
                else:
                    ch, rgb = "=", (80, 180, 255)
                color = term.color_rgb(*rgb)
            elif borders[y, x]:
                ch, rgb = "#", (160, 0, 160)
                color = term.color_rgb(*rgb)
            else:
                glyph, rgb = BIOME_GLYPHS[biome[y, x]]
                ch = glyph
                color = term.color_rgb(*rgb)
            line += color + ch + term.normal
        lines.append(line)
    print(term.home + "\n".join(lines))
