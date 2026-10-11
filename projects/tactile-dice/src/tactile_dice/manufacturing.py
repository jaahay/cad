"""Manufacturing-only orientation and sacrificial support geometry."""

from __future__ import annotations

from math import cos, radians, sin

import cadquery as cq

from .common.geometry import box_shape
from .common.parameters import HALF


SHOWCASE_ROTATION_AXIS = (1.0, 0.0, 0.0)
SHOWCASE_ROTATION_DEGREES = -135.0
SHOWCASE_DOWNWARD_EDGE = (1, 2)

SUPPORT_CONTACT_Z = 1.8
SUPPORT_PENETRATION = 0.20
SUPPORT_RAIL_LENGTH = 6.0
SUPPORT_RAIL_WIDTH = 0.8
SUPPORT_BASE_LENGTH = 18.0
SUPPORT_BASE_WIDTH = 12.0
SUPPORT_BASE_HEIGHT = 0.8


def rotate_showcase_point(
    point: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Rotate a canonical point by the showcase transform around +X."""
    x, y, z = point
    theta = radians(SHOWCASE_ROTATION_DEGREES)
    c = cos(theta)
    s = sin(theta)
    return (x, y * c - z * s, y * s + z * c)


def showcase_support() -> cq.Shape:
    """Build a broad bed foot with one deliberately narrow breakaway rail."""
    foot = box_shape(
        SUPPORT_BASE_LENGTH,
        SUPPORT_BASE_WIDTH,
        SUPPORT_BASE_HEIGHT,
        (0.0, 0.0, SUPPORT_BASE_HEIGHT / 2.0),
    )
    rail_height = SUPPORT_CONTACT_Z + SUPPORT_PENETRATION
    rail = box_shape(
        SUPPORT_RAIL_LENGTH,
        SUPPORT_RAIL_WIDTH,
        rail_height,
        (0.0, 0.0, rail_height / 2.0),
    )
    return foot.fuse(rail)


def orient_showcase_die(die: cq.Shape) -> cq.Shape:
    """Put the shared 1-2 edge down while leaving every numbered face exposed."""
    rotated = die.rotate(
        (0.0, 0.0, 0.0),
        SHOWCASE_ROTATION_AXIS,
        SHOWCASE_ROTATION_DEGREES,
    )
    z_shift = SUPPORT_CONTACT_Z - rotated.BoundingBox().zmin
    return rotated.translate((0.0, 0.0, z_shift))


def build_showcase_print(die: cq.Shape) -> cq.Shape:
    """Attach a minimal sacrificial support base to an edge-down die."""
    oriented = orient_showcase_die(die)
    model = oriented.fuse(showcase_support())
    if not model.isValid() or len(model.Solids()) != 1:
        raise ValueError("showcase support failed to form one valid printable solid")
    return model


def showcase_manifest() -> dict[str, object]:
    return {
        "name": "edge-showcase",
        "downward_edge": list(SHOWCASE_DOWNWARD_EDGE),
        "rotation_axis": "X",
        "rotation_degrees": SHOWCASE_ROTATION_DEGREES,
        "support": {
            "kind": "integrated-breakaway-rail",
            "contact": "center of shared 1-2 edge",
            "base_mm": [
                SUPPORT_BASE_LENGTH,
                SUPPORT_BASE_WIDTH,
                SUPPORT_BASE_HEIGHT,
            ],
            "rail_mm": [
                SUPPORT_RAIL_LENGTH,
                SUPPORT_RAIL_WIDTH,
            ],
            "penetration_mm": SUPPORT_PENETRATION,
        },
    }


def canonical_one_two_edge_midpoint() -> tuple[float, float, float]:
    """Canonical midpoint of the +Z/+Y edge, useful for intent validation."""
    return (0.0, HALF, HALF)
