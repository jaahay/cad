# CAD

Source-controlled parametric CAD projects and the tooling used to build and validate them.

## Projects

- [`projects/tactile-dice`](projects/tactile-dice/) — tactile, kid-friendly d6 prototypes targeting a Bambu Lab P2S workflow.
- [`projects/rotary-vault`](projects/rotary-vault/) — compact weekly rotary pill-organizer prototype with seven daily cavities plus a mechanically solid CLOSED sector.

## Repository structure

Each design lives under `projects/<project>/` with project-specific source, tests, and documentation. Repository-wide Python dependencies, export tooling, mesh validation, CI, and generated-output conventions live at the repository root.

```text
projects/<project>/
  README.md
  src/<python_package>/
  tests/

tools/
  export_project.py
  validate_mesh.py

build/<project>/
  step/
  stl/
```

Text-based parametric source is canonical. Generated manufacturing/interchange files such as STL, STEP, and 3MF are written under `build/` and are not committed. Exact prototype or print-ready binaries can be attached to tagged GitHub releases when they become useful handoff artifacts.

## Environment

The workspace uses Python 3.12+ and declares its dependencies once in the root `pyproject.toml`.

With `uv`:

```sh
uv sync
uv run pytest
uv run python tools/export_project.py tactile-dice
uv run python tools/export_project.py rotary-vault
uv run python tools/validate_mesh.py build/tactile-dice/stl
uv run python tools/validate_mesh.py build/rotary-vault/stl
```

If `make` is available, `make tactile-dice` or `make rotary-vault` generates, validates, and tests the selected project. `make clean` removes all generated output.
