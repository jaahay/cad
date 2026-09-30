# Rotary Vault

Parametric CAD for a compact weekly pill organizer built around a direct rotary interaction rather than seven individual daily lids.

## Status

**First CadQuery engineering pass.** This project is the source-controlled continuation of the first Rotary Vault engineering prototype. The port preserves the core architecture and dimensions while moving the model into the repository's normalized CadQuery workspace.

The design has not yet been physically printed. Fit, detent feel, latch feel, pill flow, and selector snap retention remain prototype-validation items.

## Interaction model

- 8 indexed positions at exactly **45°** each.
- Positions 1–7 are **MON–SUN** pill cavities.
- Position 0 is a **solid CLOSED sector**.
- The outer shell has one permanent dispensing port.
- Rotating a day behind the port exposes only that day's cavity.
- Rotating CLOSED behind the port blocks the opening with bulk carousel geometry rather than a separate shutter.
- A single weekly refill lid exposes all seven cavities for refill-by-medication.

## Current envelope

- Soft-octagonal shell: **92 mm across flats**
- Carousel: **78 mm diameter**
- Fixed shell height: **18.6 mm**
- Carousel height: **15.2 mm**
- Intended dose capacity: 6–8 ordinary tablets/capsules per day, subject to physical validation

## Source layout

```text
src/rotary_vault/
  __init__.py
  parameters.py   # canonical dimensions and 8-position indexing
  geometry.py     # geometric helpers
  body.py         # fixed shell, port, hinge, detents
  carousel.py     # 7 cavities + solid CLOSED sector
  lid.py          # captive weekly refill lid
  selector.py     # low-profile crown and keyed drive
  model.py        # project composition and invariants

tests/
  test_model.py
```

## Generate and validate

From the repository root:

```sh
uv sync
uv run pytest projects/rotary-vault/tests
uv run python tools/export_project.py rotary-vault
uv run python tools/validate_mesh.py build/rotary-vault/stl
```

Generated STEP/STL files live under `build/rotary-vault/` and are ignored by Git.
