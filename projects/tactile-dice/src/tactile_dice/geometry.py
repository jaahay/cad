"""Reusable geometric primitives for the tactile-dice family."""

import cadquery as cq

from .parameters import HALF, PIP_DEPTH, PIP_SPHERE_RADIUS, SIZE


def wp_solid(workplane: cq.Workplane) -> cq.Shape:
    return workplane.val()


def rounded_cube(radius: float) -> cq.Shape:
    return wp_solid(cq.Workplane("XY").box(SIZE, SIZE, SIZE).edges().fillet(radius))


def chamfered_cube(chamfer: float) -> cq.Shape:
    return wp_solid(cq.Workplane("XY").box(SIZE, SIZE, SIZE).edges().chamfer(chamfer))


def box_shape(x: float, y: float, z: float, translation=(0, 0, 0)) -> cq.Shape:
    return wp_solid(cq.Workplane("XY").box(x, y, z).translate(translation))


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
                    cq.Workplane("XY").sphere(radius).translate((sx * center, sy * center, sz * center))
                )
                body = body.cut(sphere)
    return body


def pip_sphere(face: str, u: float, v: float) -> cq.Shape:
    depth = HALF + PIP_SPHERE_RADIUS - PIP_DEPTH
    if face == "+Z":
        center = (u, v, depth)
    elif face == "-Z":
        center = (u, -v, -depth)
    elif face == "+Y":
        center = (u, depth, v)
    elif face == "-Y":
        center = (-u, -depth, v)
    elif face == "+X":
        center = (depth, -u, v)
    elif face == "-X":
        center = (-depth, u, v)
    else:
        raise ValueError(face)
    return wp_solid(cq.Workplane("XY").sphere(PIP_SPHERE_RADIUS).translate(center))
