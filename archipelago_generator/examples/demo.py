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
    args = parser.parse_args()
    arch = generate_archipelago(width=args.width, height=args.height, seed=args.seed)
    print(f"Generated archipelago with {len(arch.cells)} cells")
    render_archipelago(arch)


if __name__ == "__main__":
    main()

