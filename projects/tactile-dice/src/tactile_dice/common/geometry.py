"""Geometric primitives shared by tactile-dice blueprints."""

import cadquery as cq

from .parameters import (
    BUBBLE_HEIGHT,
    BUBBLE_RADIUS,
    BUTTON_EMBED,
    BUTTON_HEIGHT,
    BUTTON_RADIUS,
    HALF,
    NESTED_INNER_DEPTH,
    NESTED_INNER_PANEL,
    NESTED_OUTER_DEPTH,
    NESTED_OUTER_PANEL,
    PIP_DEPTH,
    PIP_SPHERE_RADIUS,
    SIZE,
)


FACES = ("+Z", "-Z", "+Y", "-Y", "+X", "-X")


def wp_solid(workplane: cq.Workplane) -> cq.Shape:
    return workplane.val()


def rounded_cube(radius: float) -> cq.Shape:
    return wp_solid(cq.Workplane("XY").box(SIZE, SIZE, SIZE).edges().fillet(radius))


def chamfered_cube(chamfer: float) -> cq.Shape:
    return wp_solid(cq.Workplane("XY").box(SIZE, SIZE, SIZE).edges().chamfer(chamfer))


def box_shape(x: float, y: float, z: float, translation=(0, 0, 0)) -> cq.Shape:
    return wp_solid(cq.Workplane("XY").box(x, y, z).translate(translation))


def face_point(face: str, u: float, v: float, distance: float) -> tuple[float, float, float]:
    """Map face-local coordinates to the established d6 orientation."""
    if face == "+Z":
        return (u, v, distance)
    if face == "-Z":
        return (u, -v, -distance)
    if face == "+Y":
        return (u, distance, v)
    if face == "-Y":
        return (-u, -distance, v)
    if face == "+X":
        return (distance, -u, v)
    if face == "-X":
        return (-distance, u, v)
    raise ValueError(face)


def face_normal(face: str) -> tuple[float, float, float]:
    normals = {
        "+Z": (0.0, 0.0, 1.0),
        "-Z": (0.0, 0.0, -1.0),
        "+Y": (0.0, 1.0, 0.0),
        "-Y": (0.0, -1.0, 0.0),
        "+X": (1.0, 0.0, 0.0),
        "-X": (-1.0, 0.0, 0.0),
    }
    try:
        return normals[face]
    except KeyError as exc:
        raise ValueError(face) from exc


def ring_cutter(axis: str, pos: float, width: float, depth: float) -> cq.Shape:
    """Create a rectangular ring that cuts only the outer skin of a die."""
    outer_size = SIZE + 2.0
    inner_size = SIZE - 2.0 * depth
    if axis == "Z":
        outer = box_shape(outer_size, outer_size, width, (0, 0, pos))
        inner = box_shape(inner_size, inner_size, width + 2.0, (0, 0, pos))
    elif axis == "Y":
        outer = box_shape(outer_size, width, outer_size, (0, pos, 0))
        inner = box_shape(inner_size, width + 2.0, inner_size, (0, pos, 0))
    elif axis == "X":
        outer = box_shape(width, outer_size, outer_size, (pos, 0, 0))
        inner = box_shape(width + 2.0, inner_size, inner_size, (pos, 0, 0))
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
    radius = 3.1
    center = HALF + 1.15
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                sphere = wp_solid(
                    cq.Workplane("XY")
                    .sphere(radius)
                    .translate((sx * center, sy * center, sz * center))
                )
                body = body.cut(sphere)
    return body


def face_panel_cutter(face: str, size: float, depth: float) -> cq.Shape:
    """Cut a shallow square panel inward from one nominal face."""
    extra = 1.0
    span = depth + extra
    center_distance = HALF + (extra - depth) / 2.0
    center = face_point(face, 0.0, 0.0, center_distance)

    if face.endswith("Z"):
        return box_shape(size, size, span, center)
    if face.endswith("Y"):
        return box_shape(size, span, size, center)
    if face.endswith("X"):
        return box_shape(span, size, size, center)
    raise ValueError(face)


def nested_steps_cube() -> cq.Shape:
    body = rounded_cube(3.0)
    for face in FACES:
        body = body.cut(face_panel_cutter(face, NESTED_OUTER_PANEL, NESTED_OUTER_DEPTH))
        body = body.cut(face_panel_cutter(face, NESTED_INNER_PANEL, NESTED_INNER_DEPTH))
    return body


def pip_sphere(face: str, u: float, v: float) -> cq.Shape:
    distance = HALF + PIP_SPHERE_RADIUS - PIP_DEPTH
    center = face_point(face, u, v, distance)
    return wp_solid(cq.Workplane("XY").sphere(PIP_SPHERE_RADIUS).translate(center))


def bubble_sphere(face: str, u: float, v: float) -> cq.Shape:
    distance = HALF - BUBBLE_RADIUS + BUBBLE_HEIGHT
    center = face_point(face, u, v, distance)
    return wp_solid(cq.Workplane("XY").sphere(BUBBLE_RADIUS).translate(center))


def button_cylinder(face: str, u: float, v: float) -> cq.Shape:
    origin = face_point(face, u, v, HALF - BUTTON_EMBED)
    normal = face_normal(face)
    return cq.Solid.makeCylinder(
        BUTTON_RADIUS,
        BUTTON_EMBED + BUTTON_HEIGHT,
        cq.Vector(*origin),
        cq.Vector(*normal),
    )
