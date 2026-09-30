#!/usr/bin/env python3
from pathlib import Path
import sys
import trimesh


def repair(path: Path) -> tuple[bool, bool, tuple[float, float, float]]:
    mesh = trimesh.load_mesh(path, process=False)
    mesh.merge_vertices()
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    mesh.export(path)

    check = trimesh.load_mesh(path, process=True)
    return (
        bool(check.is_watertight),
        bool(check.is_winding_consistent),
        tuple(float(x) for x in check.extents),
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "stl"
    failed = False
    for path in sorted(root.glob("*.stl")):
        watertight, winding, extents = repair(path)
        size_ok = all(abs(x - 24.0) < 0.01 for x in extents)
        ok = watertight and winding and size_ok
        print(f"{path.name}: watertight={watertight} winding={winding} extents={extents} ok={ok}")
        failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
