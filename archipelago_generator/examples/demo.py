"""Example usage of the archipelago generator."""

from __future__ import annotations

import argparse

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from archipelago_generator import generate_archipelago, render_archipelago


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate archipelago map")
    parser.add_argument("--width", type=int, default=200)
    parser.add_argument("--height", type=int, default=200)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--legend", action="store_true", help="show biome legend")
    parser.add_argument("--river-width", type=int, default=1)
    parser.add_argument("--road-width", type=int, default=1)
    parser.add_argument("--jitter", action="store_true", help="enable jitter")
    args = parser.parse_args()
    arch = generate_archipelago(
        width=args.width,
        height=args.height,
        seed=args.seed,
        river_width_tiles=args.river_width,
        road_width_tiles=args.road_width,
        jitter=args.jitter,
    )
    print(f"Generated archipelago with {len(arch.cells)} cells")
    render_archipelago(arch, show_legend=args.legend)


if __name__ == "__main__":
    main()

