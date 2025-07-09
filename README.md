# Archipelago

This project implements a procedural overworld generator as described in
`world_prd.md`. It produces deterministic fantasy maps with provinces,
rivers, and cities rendered in the terminal.

## Usage

Install dependencies:

```bash
pip install numpy perlin-noise scipy blessed
```

Generate a map:

```bash
python -m archipelago --width 80 --height 40 --seed 1 --provinces 5
```

## Tests

Run tests with:

```bash
PYTHONPATH=$PWD pytest -q
```
