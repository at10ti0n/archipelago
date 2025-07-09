from __future__ import annotations

import argparse

from .generator import generate_world
from .render import render_map


def main():
    parser = argparse.ArgumentParser(description="Generate procedural world map")
    parser.add_argument("--width", type=int, default=80)
    parser.add_argument("--height", type=int, default=40)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--provinces", type=int, default=5)
    args = parser.parse_args()
    world = generate_world(args.width, args.height, args.seed, args.provinces)
    render_map(world)


if __name__ == "__main__":
    main()
