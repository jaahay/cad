#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import trimesh


def validate(path: Path) -> tuple[bool, bool, tuple[float, float, float], int]:
    mesh = trimesh.load_mesh(path, process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError(f"{path} did not load as a single mesh")

    components = len(mesh.split(only_watertight=False))
    return (
        bool(mesh.is_watertight),
        bool(mesh.is_winding_consistent),
        tuple(float(value) for value in mesh.extents),
        components,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated STL meshes without modifying them.")
    parser.add_argument("path", type=Path, help="STL file or directory containing STL files")
    args = parser.parse_args()

    paths = [args.path] if args.path.is_file() else sorted(args.path.glob("*.stl"))
    if not paths:
        print(f"No STL files found at {args.path}")
        return 1

    failed = False
    for path in paths:
        watertight, winding, extents, components = validate(path)
        ok = watertight and winding and components == 1
        print(
            f"{path.name}: watertight={watertight} winding={winding} "
            f"components={components} extents={extents} ok={ok}"
        )
        failed |= not ok

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
