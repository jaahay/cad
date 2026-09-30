"""Captive weekly refill lid."""

from __future__ import annotations

import cadquery as cq

from .geometry import cylinder_x, cylinder_z, soft_oct_prism
from .parameters import (
    ACROSS_FLATS,
    BODY_H,
    CORNER_ROUND,
    HINGE_AXIS_Y,
    HINGE_AXIS_Z,
    HINGE_PIN_D,
    HINGE_R,
    LATCH_H,
    LATCH_HOOK,
    LATCH_T,
    LATCH_W,
    LID_KNUCKLE_LEN,
    LID_T,
    SELECTOR_HOLE_D,
)


def build_lid() -> cq.Shape:
    # Local coordinates: plate bottom is z=0. Hinge geometry may extend below it.
    lid = soft_oct_prism(LID_T, ACROSS_FLATS - 0.8, CORNER_ROUND - 0.4)

    hinge_y = HINGE_AXIS_Y
    hinge_z = HINGE_AXIS_Z - BODY_H
    outer = cylinder_x(LID_KNUCKLE_LEN, HINGE_R, (0.0, hinge_y, hinge_z))
    bore = cylinder_x(LID_KNUCKLE_LEN + 0.8, HINGE_PIN_D / 2.0, (0.0, hinge_y, hinge_z))
    lid = lid.fuse(outer.cut(bore))

    pedestal = cq.Workplane("XY").box(LID_KNUCKLE_LEN, 5.0, 3.8).val().translate(
        (0.0, ACROSS_FLATS / 2.0 + 0.5, 0.6)
    )
    lid = lid.fuse(pedestal)

    # Broad weekly-use latch tongue on front edge.
    tongue = cq.Workplane("XY").box(LATCH_W, LATCH_T, LATCH_H).val().translate(
        (0.0, -ACROSS_FLATS / 2.0 + 0.6, -0.2)
    )
    hook = cq.Workplane("XY").box(LATCH_W, LATCH_HOOK, 0.9).val().translate(
        (0.0, -ACROSS_FLATS / 2.0 + 1.0, -LATCH_H / 2.0 + 0.2)
    )
    lid = lid.fuse(tongue).fuse(hook)

    # Selector bearing hole.
    hole = cylinder_z(SELECTOR_HOLE_D / 2.0, LID_T + 2.0, -1.0)
    lid = lid.cut(hole)
    return lid
