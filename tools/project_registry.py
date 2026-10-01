"""Project discovery and the repository-facing CAD project contract."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path
import sys
import tomllib
from types import ModuleType


SUPPORTED_BACKENDS = {"cadquery"}


@dataclass(frozen=True)
class ProjectSpec:
    slug: str
    display_name: str
    backend: str
    module: str
    root: Path
    source_dir: Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def discover_projects() -> dict[str, ProjectSpec]:
    projects: dict[str, ProjectSpec] = {}

    for manifest in sorted((repo_root() / "projects").glob("*/cad.toml")):
        data = tomllib.loads(manifest.read_text(encoding="utf-8"))
        project_root = manifest.parent
        slug = data.get("slug")
        display_name = data.get("display_name")
        backend = data.get("backend")
        module = data.get("module")

        if slug != project_root.name:
            raise ValueError(
                f"{manifest}: slug {slug!r} must match directory {project_root.name!r}"
            )
        if not isinstance(display_name, str) or not display_name:
            raise ValueError(f"{manifest}: display_name is required")
        if backend not in SUPPORTED_BACKENDS:
            raise ValueError(
                f"{manifest}: unsupported backend {backend!r}; "
                f"supported backends: {sorted(SUPPORTED_BACKENDS)}"
            )
        if not isinstance(module, str) or not module:
            raise ValueError(f"{manifest}: module is required")

        source_dir = project_root / "src"
        if not source_dir.is_dir():
            raise ValueError(f"{manifest}: missing src directory")
        if slug in projects:
            raise ValueError(f"Duplicate CAD project slug: {slug}")

        projects[slug] = ProjectSpec(
            slug=slug,
            display_name=display_name,
            backend=backend,
            module=module,
            root=project_root,
            source_dir=source_dir,
        )

    return projects


def load_project_module(spec: ProjectSpec) -> ModuleType:
    source = str(spec.source_dir)
    if source not in sys.path:
        sys.path.insert(0, source)

    module = importlib.import_module(spec.module)
    for attribute in ("blueprints", "build", "validate_project"):
        if not callable(getattr(module, attribute, None)):
            raise TypeError(
                f"{spec.slug}: {spec.module} must expose callable {attribute}()"
            )
    return module
