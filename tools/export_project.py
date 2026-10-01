#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from cadquery import exporters
import trimesh

from project_registry import ProjectSpec, discover_projects, load_project_module


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


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


def export_blueprint(spec: ProjectSpec, blueprint: str) -> Path:
    module = load_project_module(spec)
    module.validate_project()

    available = tuple(module.blueprints())
    if blueprint not in available:
        raise SystemExit(
            f"Unknown blueprint {blueprint!r} for {spec.slug}; "
            f"choose from: {', '.join(available)}"
        )

    parts = module.build(blueprint)
    if not isinstance(parts, dict) or not parts:
        raise TypeError(
            f"{spec.slug}/{blueprint}: build() must return a non-empty part mapping"
        )

    output = repo_root() / "build" / spec.slug / blueprint
    step_dir = output / "step"
    stl_dir = output / "stl"
    step_dir.mkdir(parents=True, exist_ok=True)
    stl_dir.mkdir(parents=True, exist_ok=True)

    for part_name, model in parts.items():
        if not isinstance(part_name, str) or not part_name:
            raise TypeError(f"{spec.slug}/{blueprint}: invalid part name {part_name!r}")

        exporters.export(model, str(step_dir / f"{part_name}.step"))
        stl_path = stl_dir / f"{part_name}.stl"
        exporters.export(
            model,
            str(stl_path),
            tolerance=0.03,
            angularTolerance=0.08,
        )
        normalize_stl(stl_path)

    print(
        f"Exported {len(parts)} part(s) for "
        f"{spec.slug}/{blueprint} to {output.relative_to(repo_root())}"
    )
    return output


def export_project(spec: ProjectSpec, blueprint: str | None = None) -> None:
    module = load_project_module(spec)
    module.validate_project()
    available = tuple(module.blueprints())
    if not available:
        raise ValueError(f"{spec.slug}: project exposes no blueprints")

    selected = (blueprint,) if blueprint is not None else available
    for name in selected:
        export_blueprint(spec, name)


def list_projects(projects: dict[str, ProjectSpec]) -> None:
    for slug, spec in projects.items():
        module = load_project_module(spec)
        module.validate_project()
        print(f"{slug} [{spec.backend}]")
        for blueprint in module.blueprints():
            print(f"  {blueprint}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover and export CAD project blueprints to STEP and STL."
    )
    parser.add_argument("project", nargs="?", help="Project slug under projects/")
    parser.add_argument("--blueprint", help="Build only one blueprint in the project")
    parser.add_argument("--all", action="store_true", help="Build every discovered project")
    parser.add_argument("--list", action="store_true", help="List discovered projects and blueprints")
    args = parser.parse_args()

    projects = discover_projects()

    if args.list:
        if args.project or args.blueprint or args.all:
            parser.error("--list cannot be combined with build arguments")
        list_projects(projects)
        return 0

    if args.all:
        if args.project or args.blueprint:
            parser.error("--all cannot be combined with project or --blueprint")
        for spec in projects.values():
            export_project(spec)
        return 0

    if not args.project:
        parser.error("project is required unless --all or --list is used")
    if args.project not in projects:
        parser.error(
            f"unknown project {args.project!r}; choose from: {', '.join(projects)}"
        )

    export_project(projects[args.project], args.blueprint)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
