# Tactile Dice

Parametric CAD for a family of tactile d6 designs intended for simple FDM printing and kid-friendly handling.

This directory is one **project family**. The repository-facing blueprints remain the underlying body designs with classic recessed pips. A small project-specific designer can also combine any body with alternate tactile count marks without turning the repository-wide CAD contract into a configuration framework.

## Status

The current bodies generate valid solids and exported STL meshes are checked for watertightness and winding consistency. Geometry tests enforce the d6 definition, single-solid output, and design-combination validity. The designs have not yet been physically validated on the Bambu Lab P2S.

## Shared d6 definition

- Nominal body size: **24 x 24 x 24 mm**
- Values: exactly **1 through 6**, once each
- Opposites: **1↔6, 2↔5, 3↔4**
- Orientation: `+Z=1, -Z=6, +Y=2, -Y=5, +X=3, -X=4`
- No numerals
- One solid per die

## Body choices

- `mochi-soft` — 3.8 mm edge radius; soft rounded baseline
- `spherocube` — 5.8 mm edge radius; deliberately more spherical
- `facet` — 2.4 mm chamfer; crisp geometric body
- `edge-channel` — rounded body with shallow perimeter channels
- `corner-pocket` — rounded body with eight symmetric corner scallops
- `nested-steps` — two shallow inset face levels that create a tactile frame

## Count-mark choices

- `pips` — classic shallow spherical recesses
- `bubbles` — low rounded bumps
- `buttons` — broad, low flat-topped bumps

Every mark is still one countable unit. The mark shape changes; the ordinary 1–6 pip layout does not.

That gives **18 body/mark combinations** without introducing a large configuration system.

## Tactile Dice designer CLI

From the repository root:

```sh
# Interactive chooser
uv run python tools/tactile_dice.py

# See the available choices without building anything
uv run python tools/tactile_dice.py --list

# Build one explicit combination
uv run python tools/tactile_dice.py --body mochi-soft --marks bubbles

# Build all 18 combinations
uv run python tools/tactile_dice.py --all
```

With `make`:

```sh
make dice
make dice-list
make dice-all
```

Custom combinations are written under:

```text
build/tactile-dice/designs/<body>--<marks>/
  step/die.step
  stl/die.stl
```

## Repository blueprints

The normal repository exporter remains intentionally simple:

```sh
uv run python tools/export_project.py tactile-dice
uv run python tools/export_project.py tactile-dice --blueprint mochi-soft
uv run python tools/validate_mesh.py build/tactile-dice
uv run pytest projects/tactile-dice/tests
```

Each repository blueprint uses the corresponding body with classic recessed `pips`, and is generated under `build/tactile-dice/<blueprint>/`.

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
    nested_steps.py
tests/
  test_tactile_dice.py
  test_tactile_dice_cli.py
```

Generated STEP/STL outputs remain ignored build artifacts. Exact prototype or print-ready binaries can be attached to a tagged GitHub release when useful for handoff.
