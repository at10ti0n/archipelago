# Archipelago

This project implements a procedural overworld generator as described in
`prds/world_prd.md`. It produces deterministic fantasy maps with provinces,
rivers, and cities rendered in the terminal.

It also includes a basic archipelago generator following `prds/archipelago_prd.md`.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate a map:

```bash
python -m archipelago --width 80 --height 40 --seed 1 --provinces 5
```

Generate an archipelago preview:

```bash
python archipelago_generator/examples/demo.py --width 200 --height 200 --seed 42
python archipelago_generator/examples/demo.py --width 80 --height 40 --seed 42 --legend
```
The legend lists glyphs for all biomes along with markers for cities (`@`), roads
(`:`), and rivers (`=`/`≡`).

## Tests

Run tests with:

```bash
PYTHONPATH=$PWD pytest -q
```
