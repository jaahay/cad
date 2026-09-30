"""Low-profile selector crown and keyed carousel drive."""

from __future__ import annotations

import cadquery as cq

from .geometry import cylinder_z, d_prism
from .parameters import (
    DRIVE_LEN,
    D_FLAT,
    SELECTOR_BEAD_D,
    SELECTOR_BEAD_H,
    SELECTOR_D,
    SELECTOR_H,
    STEM_D,
    STEM_LEN,
)


def build_selector() -> cq.Shape:
    selector = cylinder_z(SELECTOR_D / 2.0, SELECTOR_H)
    selector = selector.fuse(cylinder_z(STEM_D / 2.0, STEM_LEN, -STEM_LEN))
    selector = selector.fuse(
        cylinder_z(SELECTOR_BEAD_D / 2.0, SELECTOR_BEAD_H, -STEM_LEN + 0.50)
    )
    selector = selector.fuse(
        d_prism(DRIVE_LEN + 0.35, STEM_D - 0.25, D_FLAT + 0.10, -STEM_LEN - DRIVE_LEN)
    )

    # Tactile grip flutes around the crown. They are shallow cuts, not separate protrusions.
    for angle in range(0, 360, 15):
        cutter = (
            cq.Workplane("XY")
            .circle(0.7)
            .extrude(SELECTOR_H + 0.6)
            .val()
            .translate((SELECTOR_D / 2.0 + 0.15, 0.0, -0.3))
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )
        selector = selector.cut(cutter)
    return selector
