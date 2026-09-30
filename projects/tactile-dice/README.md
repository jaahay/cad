# Tactile Dice

Parametric CAD for a family of tactile d6 designs intended for simple FDM printing and kid-friendly handling.

## Status

**First CAD pass.** The models generate valid 24 mm solids and exported STL meshes are checked for watertightness, winding consistency, and overall dimensions. They have not yet been validated in Bambu Studio on the P2S or physically printed.

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

The generator validates the 1–6 mapping and opposite-face rule before producing geometry.

## First body designs

- `mochi_soft` — 3.8 mm edge radius; soft rounded baseline
- `spherocube` — 5.8 mm edge radius; deliberately more spherical
- `facet` — 2.4 mm chamfer; crisp geometric body
- `edge_channel` — rounded body with shallow perimeter channels kept away from the pip field
- `corner_pocket` — rounded body with eight symmetric shallow corner scallops

## Setup

Python dependencies used for this first pass are pinned in `requirements.txt`.

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python src\dice_family.py
.venv\Scripts\python src\repair_validate_stl.py
```

macOS/Linux:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python src/dice_family.py
python src/repair_validate_stl.py
```

If `make` is available, `make all` performs the generation and STL validation steps.

## Generated files

Generation creates:

- `step/` — interoperable CAD exports
- `stl/` — slicer-ready mesh exports

These are generated artifacts and are ignored by Git by default. A later print milestone may publish exact STL/3MF files through a tagged GitHub release.

## Printer handoff

The intended first prototype workflow is deliberately plain: single material, no required paint, no support-dependent decorative features, and minimal post-processing. The next manufacturing validation step is to load the generated models into Bambu Studio, inspect orientation/layers for the Bambu Lab P2S, and then physically prototype the selected bodies.
