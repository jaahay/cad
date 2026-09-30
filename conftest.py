"""Pytest bootstrap for independently packaged CAD projects."""

from __future__ import annotations

from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parent


for manifest in sorted((ROOT / "projects").glob("*/cad.toml")):
    data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    project_dir = manifest.parent
    if data.get("slug") != project_dir.name:
        raise RuntimeError(
            f"{manifest}: slug must match project directory {project_dir.name!r}"
        )

    source_dir = project_dir / "src"
    if not source_dir.is_dir():
        raise RuntimeError(f"{manifest}: missing src directory")

    source = str(source_dir)
    if source not in sys.path:
        sys.path.insert(0, source)
