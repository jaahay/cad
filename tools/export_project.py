#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
from pathlib import Path
import sys

from cadquery import exporters
import trimesh


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def package_name(project: str) -> str:
    return project.replace("-", "_")


def load_models(project: str):
    root = repo_root()
    source_dir = root / "projects" / project / "src"
    if not source_dir.is_dir():
        raise SystemExit(f"Unknown CAD project: {project}")

    sys.path.insert(0, str(source_dir))
    module = importlib.import_module(f"{package_name(project)}.model")
    return module.build_all()


def normalize_stl(path: Path) -> None:
    """Normalize exporter topology without changing the intended CAD surface."""
    mesh = trimesh.load_mesh(path, process=False)
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError(f"{path} did not load as a single mesh")
    mesh.merge_vertices()
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    mesh.export(path)


def export_project(project: str) -> Path:
    root = repo_root()
    output = root / "build" / project
    step_dir = output / "step"
    stl_dir = output / "stl"
    step_dir.mkdir(parents=True, exist_ok=True)
    stl_dir.mkdir(parents=True, exist_ok=True)

    models = load_models(project)
    for name, model in models.items():
        exporters.export(model, str(step_dir / f"{name}.step"))
        stl_path = stl_dir / f"{name}.stl"
        exporters.export(
            model,
            str(stl_path),
            tolerance=0.03,
            angularTolerance=0.08,
        )
        normalize_stl(stl_path)

    print(f"Exported {len(models)} model(s) to {output.relative_to(root)}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Export one CAD project to STEP and STL.")
    parser.add_argument("project", help="Project directory name under projects/")
    args = parser.parse_args()
    export_project(args.project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
