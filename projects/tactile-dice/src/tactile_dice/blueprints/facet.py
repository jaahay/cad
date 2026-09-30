"""Crisp chamfered tactile-die blueprint."""

import cadquery as cq

from ..common.die import finish_die
from ..common.geometry import chamfered_cube


def build() -> dict[str, cq.Shape]:
    return {"die": finish_die(chamfered_cube(2.4))}
