"""Low-level geometry helpers for the Rotary Vault."""

from __future__ import annotations

import math
from collections.abc import Iterable

import cadquery as cq

from .parameters import ARC_SEGMENTS, regular_octagon_circumradius


def shape_of(workplane: cq.Workplane) -> cq.Shape:
    return workplane.val()


def fuse_all(shapes: Iterable[cq.Shape]) -> cq.Shape:
    iterator = iter(shapes)
    result = next(iterator)
    for shape in iterator:
        result = result.fuse(shape)
    return result


def soft_oct_prism(height: float, across_flats: float, corner_radius: float) -> cq.Shape:
    radius = regular_octagon_circumradius(across_flats)
    points = [
        (
            radius * math.cos(math.radians(22.5 + index * 45.0)),
            radius * math.sin(math.radians(22.5 + index * 45.0)),
        )
        for index in range(8)
    ]
    solid = cq.Workplane("XY").polyline(points).close().extrude(height)
    if corner_radius > 0:
        solid = solid.edges("|Z").fillet(corner_radius)
    return shape_of(solid)


def cylinder_z(radius: float, height: float, z: float = 0.0) -> cq.Shape:
    return shape_of(cq.Workplane("XY").workplane(offset=z).circle(radius).extrude(height))


def cylinder_x(length: float, radius: float, center: tuple[float, float, float]) -> cq.Shape:
    # Build along +Z, center it at the origin, then rotate onto X.
    shape = shape_of(cq.Workplane("XY").circle(radius).extrude(length)).translate((0, 0, -length / 2.0))
    shape = shape.rotate((0, 0, 0), (0, 1, 0), 90.0)
    return shape.translate(center)


def rounded_box(
    size: tuple[float, float, float],
    radius: float,
    center: tuple[float, float, float],
) -> cq.Shape:
    x, y, z = size
    shape = cq.Workplane("XY").box(x, y, z)
    if radius > 0:
        shape = shape.edges("|Z").fillet(radius)
    return shape_of(shape).translate(center)


def sphere(radius: float, center: tuple[float, float, float]) -> cq.Shape:
    return shape_of(cq.Workplane("XY").sphere(radius)).translate(center)


def annular_sector_prism(
    r0: float,
    r1: float,
    center_angle_deg: float,
    half_angle_deg: float,
    height: float,
    z0: float = 0.0,
) -> cq.Shape:
    a0 = center_angle_deg - half_angle_deg
    a1 = center_angle_deg + half_angle_deg
    outer = [
        (
            r1 * math.cos(math.radians(a0 + (a1 - a0) * i / ARC_SEGMENTS)),
            r1 * math.sin(math.radians(a0 + (a1 - a0) * i / ARC_SEGMENTS)),
        )
        for i in range(ARC_SEGMENTS + 1)
    ]
    inner = [
        (
            r0 * math.cos(math.radians(a1 - (a1 - a0) * i / ARC_SEGMENTS)),
            r0 * math.sin(math.radians(a1 - (a1 - a0) * i / ARC_SEGMENTS)),
        )
        for i in range(ARC_SEGMENTS + 1)
    ]
    return shape_of(cq.Workplane("XY").workplane(offset=z0).polyline(outer + inner).close().extrude(height))


def sloped_sector_void(
    r0: float,
    r1: float,
    center_angle_deg: float,
    half_angle_deg: float,
    floor_inner: float,
    floor_outer: float,
    top: float,
) -> cq.Shape:
    """Sector volume above a planar floor sloping from hub to outside."""
    sector = annular_sector_prism(r0, r1, center_angle_deg, half_angle_deg, top + 2.0, z0=0.0)

    # In local radial coordinates, create the volume above the desired floor.
    radial_pad = 4.0
    width = 2.0 * (r1 * math.sin(math.radians(half_angle_deg)) + radial_pad)
    profile = [
        (r0 - radial_pad, floor_inner),
        (r1 + radial_pad, floor_outer),
        (r1 + radial_pad, top + 2.0),
        (r0 - radial_pad, top + 2.0),
    ]
    wedge = shape_of(
        cq.Workplane("XZ")
        .polyline(profile)
        .close()
        .extrude(width / 2.0, both=True)
    )
    wedge = wedge.rotate((0, 0, 0), (0, 0, 1), center_angle_deg)
    return sector.intersect(wedge)


def d_prism(height: float, diameter: float, flat: float, z0: float = 0.0) -> cq.Shape:
    """Circular prism with one flattened +X side."""
    circle = cylinder_z(diameter / 2.0, height, z0)
    radius = diameter / 2.0
    keep_width = diameter - flat
    max_x = radius - flat
    min_x = -radius
    center_x = (min_x + max_x) / 2.0
    box = shape_of(cq.Workplane("XY").box(keep_width, diameter + 2.0, height)).translate(
        (center_x, 0.0, z0 + height / 2.0)
    )
    # The box removes `flat` millimetres from the +X side of the circular profile.
    return circle.intersect(box)
