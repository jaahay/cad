# Tactile Dice

Parametric CAD for a family of tactile d6 designs intended for simple FDM printing and kid-friendly handling.

The normal experience is intentionally simple: make one die, or create a prototype batch that changes one playful trait at a time.

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

Start from one of the six familiar presets, or choose **Build your own** and compose the body from semantic traits:

- **Base character** — Balanced, Mochi, Spherocube, or Faceted.
- **Edge treatment** — Plain or Channels.
- **Corner treatment** — Plain or Pockets.
- **Face treatment** — Plain or Nested Steps.
- **Number style** — Recessed pips, Bubbles, Buttons, or Paws.
- **Tactile intensity** — Gentle, Standard, or Bold.

The CAD-facing dimensions behind those choices stay internal. For example, users choose **Channels**, not a groove width in millimeters. Compatibility is likewise handled by the grammar: **Pockets** are hidden for the very round Mochi and Spherocube bases because they would add little useful geometry, and **Nested Steps** are hidden there because the current panel proportions would shrink the nominal 24 mm envelope.

The first grammar exposes **20 safe body configurations × 4 number styles × 3 intensities = 240 build-your-own designs**. Standard intensity remains the original/default mark geometry.

A neutral print handoff looks like:

```text
build/tactile-dice/handoffs/mochi-soft--paws--bold/
  manifest.json
  step/die.step
  stl/die.stl
  print/showcase.stl
```

The manifest records all three design traits. The canonical STEP/STL stay unchanged. The recommended print file is `print/showcase.stl`: the die is rotated onto the shared **1–2 edge** and attached to a narrow sacrificial rail on a small bed foot, so no numbered face is used as the build-plate face.

The support is deliberately a manufacturing derivative, not part of the canonical die. Snap/cut it off after printing and lightly deburr the contacted edge if needed.

### Post-processing and painting

The default target is **usable straight from the printer**. Sanding is not part of the normal workflow. After removing the showcase support, only spot-deburr the contacted edge if it is actually rough; do not sand whole faces or tactile marks just to make the design work.

Painting is optional and should stay similarly low-friction. For the next production run, useful comparisons are:

- **Unpainted** — the control; judge the print as-produced.
- **Recessed paint fill** — dab acrylic paint into recessed pips/grooves and wipe the surrounding face clean.
- **Raised-detail accent** — lightly dry-brush or otherwise accent paws, bubbles, terraces, or other raised features.

No primer/full-body sanding pipeline is assumed. Future CAD should prefer clean support removal, printable surfaces, and features that can accept selective paint without depending on hand finishing.

### Prototype batch

Choose a baseline die, then choose exactly one trait to change:

- **Shape** — keep number style and intensity fixed.
- **Number style** — keep shape and intensity fixed.
- **Tactile intensity** — compare Gentle, Standard, and Bold while keeping shape and number style fixed.
- **Surprise one trait** — let the designer pick one of those three traits to explore.

Candidate **A** is always the baseline. Every other candidate changes only the selected trait.

A batch looks like:

```text
build/tactile-dice/prototype-batches/mochi-soft--paws--standard--vary-intensity/
  batch.json
  README.md
  candidates/
    A-mochi-soft--paws--standard/
      manifest.json
      step/die.step
      stl/die.stl
    B-.../
    C-.../
  plate/
    A-mochi-soft--paws--standard.stl
    B-....stl
    C-....stl
```

The `plate/` directory is intentionally flat: select all of its STLs and open or drag them into Bambu Studio together. Batch plate files use the same edge-down showcase geometry so the next comparison run exercises the support/orientation strategy consistently.

There is **no `.3mf` generation** and no Bambu-specific project encoding. The CAD workspace owns geometry and neutral manufacturing handoff; the slicer owns slicing and plate state.

## What the files mean

- **CadQuery `.py` source** — the parametric CAD definition and the actual design authority in this repository.
- **STEP (`.step` / `.stp`)** — precise solid/B-rep interchange geometry; appropriate when another CAD program needs an editable solid.
- **STL (`.stl`)** — a triangulated surface mesh for slicing/printing. `stl/die.stl` is the canonical die mesh.
- **`print/showcase.stl`** — a derived STL for manufacturing: same die geometry, rotated and carrying the sacrificial support base.

Other formats exist (OBJ for general meshes, DXF/SVG for 2D geometry, IGES as older CAD interchange), but this project intentionally needs only source + STEP + STL for this workflow.

## Current design choices

The six original bodies remain available as **presets**:

- **Mochi** — soft and rounded
- **Spherocube** — very round and smooth
- **Faceted** — crisp angled edges
- **Edge Channels** — grooves around the edges
- **Corner Pockets** — scooped corners
- **Nested Steps** — layered tactile faces

Build-your-own bodies use the bounded Base + Edge + Corner + Face grammar above. Raw radii, groove depths, pocket dimensions, and panel depths are deliberately not user-facing controls.

Number styles:

- **Recessed pips** — classic dice
- **Bubbles** — smooth raised bumps
- **Buttons** — broad flat bumps
- **Paws** — chunky raised paw prints

Tactile intensity:

- **Gentle** — low-profile tactile marks
- **Standard** — the familiar default feel
- **Bold** — extra-pronounced tactile marks

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

# Export one preset combination; omitted intensity defaults to Standard
./dice --body mochi-soft --numbers paws
./dice --body mochi-soft --numbers paws --intensity bold

# Compose a body without exposing CAD dimensions
./dice --base balanced --edge channels --face nested --numbers paws
./dice --base faceted --corner pockets --numbers pips --intensity bold

# Create one neutral print handoff
./dice --body mochi-soft --numbers paws --intensity bold --handoff

# Create baseline-first one-trait comparison batches
./dice --body mochi-soft --numbers paws --batch shape
./dice --body mochi-soft --numbers paws --batch numbers
./dice --body mochi-soft --numbers paws --batch intensity
./dice --body mochi-soft --numbers paws --batch surprise

# Export all 240 public build-your-own combinations
./dice --all
```

On Windows PowerShell, use `.\\dice` in place of `./dice`.

Raw combinations are written under:

```text
build/tactile-dice/designs/<body-id>--<number-style-id>--<intensity-id>/
  step/die.step
  stl/die.stl
```

Prototype batches still use named preset bodies in this incremental grammar step; component-level Base/Edge/Corner/Face mutation is the next step on issue #16.

## Repository blueprints

The repository-facing blueprint model remains deliberately simpler than the interactive designer. Each blueprint is one underlying shape using classic recessed pips at Standard intensity.

```sh
uv run python tools/export_project.py tactile-dice
uv run python tools/export_project.py tactile-dice --blueprint mochi-soft
uv run python tools/validate_mesh.py build/tactile-dice
uv run pytest projects/tactile-dice/tests
```

Generated STEP/STL outputs remain ignored build artifacts. Exact prototype or print-ready binaries can be attached to a tagged GitHub release when useful for handoff.
