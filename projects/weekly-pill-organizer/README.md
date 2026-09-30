# Weekly Pill Organizer

Parametric CAD for weekly pill-organizer concepts. This is the **project family**; individual mechanical approaches live beneath it as blueprints.

The current blueprint is **Rotary Vault**. Future viable concepts can coexist here without turning one solution into the identity of the whole project.

## Blueprints

### `rotary-vault`

A compact weekly organizer built around a direct rotary interaction rather than seven individual daily lids.

Current architecture:

- 8 indexed positions at exactly **45°** each
- positions 1–7 are **MON–SUN** pill cavities
- position 0 is a **solid CLOSED sector**
- one permanent dispensing port in the fixed outer shell
- rotating a day behind the port exposes that day's cavity
- rotating CLOSED behind the port blocks access with bulk carousel geometry
- one weekly refill lid exposes all seven daily cavities
- direct keyed selector drive

Current nominal envelope:

- soft-octagonal shell: **92 mm across flats**
- carousel: **78 mm diameter**
- fixed shell height: **18.6 mm**
- carousel height: **15.2 mm**
- intended capacity: roughly 6–8 ordinary tablets/capsules per day, pending physical validation

The design has not yet been physically printed. Fit, detent feel, latch feel, pill flow, and selector snap retention remain prototype-validation items.

## Source layout

```text
cad.toml
src/weekly_pill_organizer/
  project.py
  blueprints/
    rotary_vault/
      parameters.py
      geometry.py
      body.py
      carousel.py
      lid.py
      selector.py
      model.py
tests/
  test_weekly_pill_organizer.py
```

There is intentionally no project-level `common/` package yet. Rotary Vault is the only blueprint, so extracting shared pill-organizer geometry would be premature. Shared modules should appear only after a second blueprint proves the commonality.

## Generate and validate

From the repository root:

```sh
uv run python tools/export_project.py weekly-pill-organizer
uv run python tools/export_project.py weekly-pill-organizer --blueprint rotary-vault
uv run python tools/validate_mesh.py build/weekly-pill-organizer
uv run pytest projects/weekly-pill-organizer/tests
```

Rotary Vault exports four production parts under `build/weekly-pill-organizer/rotary-vault/{step,stl}`: body, carousel, lid, and selector.
