# Tactile Dice

Parametric CAD for a family of tactile d6 designs intended for simple FDM printing and kid-friendly handling.

The normal experience is intentionally simple: make one die, or create a prototype batch that changes one thing at a time.

## Start here

From the repository root:

**Windows PowerShell**

```powershell
.\\dice
```

**macOS / Linux**

```sh
./dice
```

The designer opens with two workflows:

```text
Tactile Dice
Make one die or compare a controlled set of variants.

What would you like to make?
  1) Make one die        Create a neutral print handoff.
  2) Prototype batch     Compare one controlled change on one plate.
```

### Make one die

Choose a friendly shape and number style, confirm it, and the designer creates a neutral print handoff:

```text
build/tactile-dice/handoffs/mochi-soft--bubbles/
  manifest.json
  step/die.step
  stl/die.stl
```

The CLI tells you which STL to open in Bambu Studio and preserves the STEP file for editable CAD.

### Prototype batch

Choose a baseline die, then choose one axis to vary:

- **Shape** — keep the number style fixed and compare every shape.
- **Number style** — keep the shape fixed and compare every number style.

Candidate **A** is always the baseline. Every other candidate changes only the selected axis.

A batch looks like:

```text
build/tactile-dice/prototype-batches/mochi-soft--bubbles--vary-shape/
  batch.json
  README.md
  candidates/
    A-mochi-soft--bubbles/
      manifest.json
      step/die.step
      stl/die.stl
    B-.../
    C-.../
  plate/
    A-mochi-soft--bubbles.stl
    B-....stl
    C-....stl
```

The `plate/` directory is intentionally flat: select all of its STLs and open or drag them into Bambu Studio together.

There is **no `.3mf` generation** and no Bambu-specific project encoding. The CAD workspace owns geometry and neutral manufacturing handoff; the slicer owns slicing and plate state.

## Current design choices

There are currently **6 shapes x 3 number styles = 18 combinations**.

Shapes:

- **Mochi** — soft and rounded
- **Spherocube** — very round and smooth
- **Faceted** — crisp angled edges
- **Edge Channels** — grooves around the edges
- **Corner Pockets** — scooped corners
- **Nested Steps** — layered tactile faces

Number styles:

- **Recessed pips** — classic dice
- **Bubbles** — smooth raised bumps
- **Buttons** — broad flat bumps

Every design keeps the same d6 rules:

- nominal body size: **24 x 24 x 24 mm**
- values **1 through 6**, once each
- opposite faces **1↔6, 2↔5, 3↔4**
- no numerals
- one solid per die

## Advanced / scripted use

Friendly labels are for the interactive UI. Stable ids remain available for scripts:

```sh
# Show names, descriptions, and ids
./dice --list

# Export raw CAD files for one combination
./dice --body mochi-soft --numbers bubbles

# Create one neutral print handoff
./dice --body mochi-soft --numbers bubbles --handoff

# Create a baseline-first comparison batch
./dice --body mochi-soft --numbers bubbles --batch shape
./dice --body mochi-soft --numbers bubbles --batch numbers

# Export all 18 raw combinations
./dice --all
```

On Windows PowerShell, use `.\\dice` in place of `./dice`.

Raw combinations remain under:

```text
build/tactile-dice/designs/<shape-id>--<number-style-id>/
  step/die.step
  stl/die.stl
```

## Repository blueprints

The repository-facing blueprint model remains deliberately simpler than the interactive designer. Each blueprint is one underlying shape using classic recessed pips.

```sh
uv run python tools/export_project.py tactile-dice
uv run python tools/export_project.py tactile-dice --blueprint mochi-soft
uv run python tools/validate_mesh.py build/tactile-dice
uv run pytest projects/tactile-dice/tests
```

Generated STEP/STL outputs remain ignored build artifacts. Exact prototype or print-ready binaries can be attached to a tagged GitHub release when useful for handoff.
