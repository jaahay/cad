#!/usr/bin/env python3
from pathlib import Path
import cadquery as cq
from cadquery import exporters

SIZE = 24.0
HALF = SIZE / 2.0
PIP_OFFSET = 4.7
PIP_SPHERE_RADIUS = 2.4
PIP_DEPTH = 0.9

# Standard d6 layout chosen for this family:
# +Z=1, -Z=6, +Y=2, -Y=5, +X=3, -X=4.
# Opposite faces sum to 7.
FACE_VALUES = {
    "+Z": 1,
    "-Z": 6,
    "+Y": 2,
    "-Y": 5,
    "+X": 3,
    "-X": 4,
}

PIPS = {
    1: [(0, 0)],
    2: [(-1, 1), (1, -1)],
    3: [(-1, 1), (0, 0), (1, -1)],
    4: [(-1, 1), (1, 1), (-1, -1), (1, -1)],
    5: [(-1, 1), (1, 1), (0, 0), (-1, -1), (1, -1)],
    6: [(-1, 1), (-1, 0), (-1, -1), (1, 1), (1, 0), (1, -1)],
}

OPPOSITE_FACES = (("+Z", "-Z"), ("+Y", "-Y"), ("+X", "-X"))


def validate_definition() -> None:
    values = sorted(FACE_VALUES.values())
    if values != [1, 2, 3, 4, 5, 6]:
        raise ValueError(f"FACE_VALUES must contain 1 through 6 exactly once; got {values}")
    for value in range(1, 7):
        if len(PIPS[value]) != value:
            raise ValueError(f"Pip layout for {value} contains {len(PIPS[value])} marks")
    for a, b in OPPOSITE_FACES:
        if FACE_VALUES[a] + FACE_VALUES[b] != 7:
            raise ValueError(f"Opposite faces {a}/{b} do not sum to 7")


def wp_solid(wp: cq.Workplane) -> cq.Shape:
    return wp.val()


def rounded_cube(radius: float) -> cq.Shape:
    return wp_solid(cq.Workplane("XY").box(SIZE, SIZE, SIZE).edges().fillet(radius))


def chamfered_cube(chamfer: float) -> cq.Shape:
    return wp_solid(cq.Workplane("XY").box(SIZE, SIZE, SIZE).edges().chamfer(chamfer))


def box_shape(x: float, y: float, z: float, translation=(0, 0, 0)) -> cq.Shape:
    return wp_solid(cq.Workplane("XY").box(x, y, z).translate(translation))


def ring_cutter(axis: str, pos: float, width: float, depth: float) -> cq.Shape:
    # Rectangular ring cutting only the outer skin; the central face region is untouched.
    o = SIZE + 2.0
    i = SIZE - 2.0 * depth
    if axis == "Z":
        outer = box_shape(o, o, width, (0, 0, pos))
        inner = box_shape(i, i, width + 2.0, (0, 0, pos))
    elif axis == "Y":
        # Create in XYZ, with Y as the thin dimension.
        outer = box_shape(o, width, o, (0, pos, 0))
        inner = box_shape(i, width + 2.0, i, (0, pos, 0))
    elif axis == "X":
        outer = box_shape(width, o, o, (pos, 0, 0))
        inner = box_shape(width + 2.0, i, i, (pos, 0, 0))
    else:
        raise ValueError(axis)
    return outer.cut(inner)


def edge_channel_cube() -> cq.Shape:
    body = rounded_cube(3.0)
    for axis in ("X", "Y", "Z"):
        for pos in (-7.8, 7.8):
            body = body.cut(ring_cutter(axis, pos, width=1.35, depth=0.55))
    return body


def corner_pocket_cube() -> cq.Shape:
    body = rounded_cube(3.2)
    r = 3.1
    c = HALF + 1.15
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                sphere = wp_solid(cq.Workplane("XY").sphere(r).translate((sx*c, sy*c, sz*c)))
                body = body.cut(sphere)
    return body


def pip_sphere(face: str, u: float, v: float) -> cq.Shape:
    d = HALF + PIP_SPHERE_RADIUS - PIP_DEPTH
    if face == "+Z": c = (u, v, d)
    elif face == "-Z": c = (u, -v, -d)
    elif face == "+Y": c = (u, d, v)
    elif face == "-Y": c = (-u, -d, v)
    elif face == "+X": c = (d, -u, v)
    elif face == "-X": c = (-d, u, v)
    else: raise ValueError(face)
    return wp_solid(cq.Workplane("XY").sphere(PIP_SPHERE_RADIUS).translate(c))


def add_face_pips(body: cq.Shape, face: str, value: int) -> cq.Shape:
    for a, b in PIPS[value]:
        body = body.cut(pip_sphere(face, a * PIP_OFFSET, b * PIP_OFFSET))
    return body


def finish_die(body: cq.Shape) -> cq.Shape:
    for face, value in FACE_VALUES.items():
        body = add_face_pips(body, face, value)
    return body


def build_all():
    validate_definition()
    return {
        "mochi_soft": finish_die(rounded_cube(3.8)),
        "spherocube": finish_die(rounded_cube(5.8)),
        "facet": finish_die(chamfered_cube(2.4)),
        "edge_channel": finish_die(edge_channel_cube()),
        "corner_pocket": finish_die(corner_pocket_cube()),
    }


def export_all(root: Path):
    (root / "step").mkdir(parents=True, exist_ok=True)
    (root / "stl").mkdir(parents=True, exist_ok=True)
    models = build_all()
    for name, model in models.items():
        exporters.export(model, str(root / "step" / f"{name}.step"))
        exporters.export(model, str(root / "stl" / f"{name}.stl"), tolerance=0.03, angularTolerance=0.08)
    return models


if __name__ == "__main__":
    export_all(Path(__file__).resolve().parents[1])
