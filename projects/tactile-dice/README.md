# Tactile Dice

Parametric CAD for a family of tactile d6 designs intended for simple FDM printing and kid-friendly handling.

This directory is one **project family**. Its alternative viable die bodies are **blueprints** within that project rather than separate projects.

## Status

**First CAD pass.** The current blueprints generate valid 24 mm solids and exported STL meshes are checked for watertightness and winding consistency. Geometry tests enforce the d6 definition, one-solid output, and nominal 24 mm envelope. The designs have not yet been validated in Bambu Studio on the P2S or physically printed.

The first pass deliberately uses conventional recessed circular pips on every body. This isolates the underlying body geometry before combining it with Paw, Critter, or other tactile-count motifs.

## Shared d6 definition

- Nominal size: **24 x 24 x 24 mm**
- Values: exactly **1 through 6**, once each
- Opposites: **1↔6, 2↔5, 3↔4**
- Orientation: `+Z=1, -Z=6, +Y=2, -Y=5, +X=3, -X=4`
- Pip style: shallow spherical recess
- Pip depth: **0.9 mm**
- Pip pitch from face center: **4.7 mm**
- No numerals
- One solid per die

## Blueprints

- `mochi-soft` — 3.8 mm edge radius; soft rounded baseline
- `spherocube` — 5.8 mm edge radius; deliberately more spherical
- `facet` — 2.4 mm chamfer; crisp geometric body
- `edge-channel` — rounded body with shallow perimeter channels kept away from the pip field
- `corner-pocket` — rounded body with eight symmetric shallow corner scallops

## Source layout

```text
cad.toml
src/tactile_dice/
  project.py
  common/
    parameters.py
    geometry.py
    die.py
  blueprints/
    mochi.py
    spherocube.py
    facet.py
    edge_channel.py
    corner_pocket.py
tests/
  test_tactile_dice.py
```

`common/` contains only geometry and rules shared by multiple tactile-dice blueprints. Each blueprint exposes its own build function.

## Generate and validate

From the repository root:

```sh
uv run python tools/export_project.py tactile-dice
uv run python tools/export_project.py tactile-dice --blueprint mochi-soft
uv run python tools/validate_mesh.py build/tactile-dice
uv run pytest projects/tactile-dice/tests
```

Generated outputs are placed under `build/tactile-dice/<blueprint>/{step,stl}` and ignored by Git.

## Printer handoff

The intended first prototype workflow is deliberately plain: single material, no required paint, no support-dependent decorative features, and minimal post-processing. The next manufacturing validation step is to load generated models into Bambu Studio, inspect orientation and layers for the Bambu Lab P2S, and physically prototype selected blueprints.
