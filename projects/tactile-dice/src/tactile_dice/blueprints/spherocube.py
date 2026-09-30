"""More spherical tactile-die blueprint."""

import cadquery as cq

from ..common.die import finish_die
from ..common.geometry import rounded_cube


def build() -> dict[str, cq.Shape]:
    return {"die": finish_die(rounded_cube(5.8))}
