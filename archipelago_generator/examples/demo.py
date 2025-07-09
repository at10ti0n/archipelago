"""Example usage of the archipelago generator."""

from __future__ import annotations

import argparse

from archipelago_generator import generate_archipelago


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate archipelago map")
    parser.add_argument("--width", type=int, default=200)
    parser.add_argument("--height", type=int, default=200)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    arch = generate_archipelago(width=args.width, height=args.height, seed=args.seed)
    print(f"Generated archipelago with {len(arch.cells)} cells")


if __name__ == "__main__":
    main()

