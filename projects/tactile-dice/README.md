# Tactile Dice

Parametric CAD for a family of tactile d6 designs intended for simple FDM printing and kid-friendly handling.

The normal experience is intentionally simple: choose a **shape**, choose how the **numbers feel**, confirm, and create the files.

## Create a die

From the repository root:

**Windows PowerShell**

```powershell
.\dice
```

**macOS / Linux**

```sh
./dice
```

The designer presents friendly names rather than source-code identifiers:

```text
Tactile Dice
Choose a shape and number style. You can go back before creating.

Choose a shape:
  1) Mochi            Soft and rounded.
  2) Spherocube       Very round and smooth.
  3) Faceted          Crisp angled edges.
  4) Edge Channels    Grooves around the edges.
  5) Corner Pockets   Scooped corners.
  6) Nested Steps     Layered tactile faces.
```

After choosing a shape, choose one of:

- **Recessed pips** — classic dice
- **Bubbles** — smooth raised bumps
- **Buttons** — broad flat bumps

The designer then shows the selection and asks for confirmation. **Back** returns to the previous choice and **Quit** exits without generating anything.

After creation it tells you exactly which file to open in Bambu Studio and where the editable STEP file lives.

## Design choices

There are currently **6 shapes x 3 number styles = 18 combinations**.

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

# Build one combination without prompts
./dice --body mochi-soft --numbers bubbles

# Build every combination
./dice --all
```

On Windows PowerShell, use `.\dice` in place of `./dice`.

Generated combinations are written under:

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
