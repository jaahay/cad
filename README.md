# CAD

Source-controlled parametric CAD projects and the tooling used to build and validate them.

## Model

The repository is organized as:

```text
repository
  project family
    blueprint
      printable part(s)
```

A **project** represents a product or design family. A **blueprint** is one viable design within that family. A blueprint may be a single simple model or a multi-part mechanical assembly.

Each project declares one modeling backend in `cad.toml`. Current projects use CadQuery; blueprints within a project do not mix CAD backends.

## Projects

- [`projects/tactile-dice`](projects/tactile-dice/) — tactile d6 design family with multiple body blueprints.
- [`projects/weekly-pill-organizer`](projects/weekly-pill-organizer/) — weekly pill-organizer design family; currently contains the Rotary Vault blueprint.

## Repository structure

```text
projects/<project>/
  cad.toml
  README.md
  src/<python_package>/
    project.py
    blueprints/
    common/              # only when multiple blueprints genuinely share domain geometry
  tests/

tools/
  project_registry.py
  export_project.py
  validate_mesh.py

build/<project>/<blueprint>/
  step/
  stl/
```

`project.py` is the stable repository-facing contract. Each project exposes its blueprint names, validates its project-level invariants, and builds one requested blueprint. Internal module layout may grow with the design: a simple blueprint can be one module while a mechanical assembly can be a package containing several physical parts.

Text-based parametric source is canonical. Generated manufacturing/interchange files such as STL, STEP, and 3MF are written under `build/` and are not committed. Exact prototype or print-ready binaries can be attached to tagged GitHub releases when useful for handoff.

## Environment

The workspace uses Python 3.12+ and declares repository tooling dependencies once in the root `pyproject.toml`.

With `uv`:

```sh
uv sync
uv run pytest
uv run python tools/export_project.py --list
uv run python tools/export_project.py tactile-dice
uv run python tools/export_project.py weekly-pill-organizer --blueprint rotary-vault
uv run python tools/export_project.py --all
uv run python tools/validate_mesh.py build
```

With `make`:

```sh
make list
make build PROJECT=tactile-dice
make build PROJECT=weekly-pill-organizer BLUEPRINT=rotary-vault
make all
make clean
```

Adding a future project should normally require only a new `projects/<project>/` tree and its `cad.toml`; CI and build tooling discover projects rather than maintaining a hard-coded project list.
