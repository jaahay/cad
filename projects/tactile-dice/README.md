# Tactile Dice

Parametric CAD for a family of tactile d6 designs intended for simple FDM printing and kid-friendly handling.

## Status

**First CAD pass.** The models generate valid 24 mm solids and exported STL meshes are checked for watertightness and winding consistency. Geometry tests also enforce the d6 definition, one-solid output, and nominal 24 mm envelope. The designs have not yet been validated in Bambu Studio on the P2S or physically printed.

The first pass deliberately uses conventional recessed circular pips on every body. This isolates the underlying body geometry before combining it with Paw, Critter, or other tactile-count motifs.

## Shared geometry

- Nominal size: **24 x 24 x 24 mm**
- Values: exactly **1 through 6**, once each
- Opposites: **1↔6, 2↔5, 3↔4**
- Orientation: `+Z=1, -Z=6, +Y=2, -Y=5, +X=3, -X=4`
- Pip style: shallow spherical recess
- Pip depth: **0.9 mm**
- Pip pitch from face center: **4.7 mm**
- No numerals
- One solid per die

## First body designs

- `mochi_soft` — 3.8 mm edge radius; soft rounded baseline
- `spherocube` — 5.8 mm edge radius; deliberately more spherical
- `facet` — 2.4 mm chamfer; crisp geometric body
- `edge_channel` — rounded body with shallow perimeter channels kept away from the pip field
- `corner_pocket` — rounded body with eight symmetric shallow corner scallops

## Source layout

Project-specific design code lives in the importable `tactile_dice` package:

```text
src/tactile_dice/
  __init__.py
  parameters.py   # canonical dimensions and d6 mappings
  geometry.py     # geometric primitives
  model.py        # model composition and design validation

tests/
  test_model.py
```

Repository-wide dependency management, export behavior, mesh validation, and CI live at the repository root rather than being duplicated in this project.

## Generate and validate

From the repository root:

```sh
uv sync
uv run pytest projects/tactile-dice/tests
uv run python tools/export_project.py tactile-dice
uv run python tools/validate_mesh.py build/tactile-dice/stl
```

Or, with `make` available:

```sh
make tactile-dice
```

Generated outputs are placed under `build/tactile-dice/{step,stl}` and ignored by Git. Exact prototype or print-ready binaries can be attached to a tagged GitHub release when useful for handoff.

## Printer handoff

The intended first prototype workflow is deliberately plain: single material, no required paint, no support-dependent decorative features, and minimal post-processing. The next manufacturing validation step is to load the generated models into Bambu Studio, inspect orientation and layers for the Bambu Lab P2S, and physically prototype the selected bodies.
