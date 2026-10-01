"""Rounded tactile die with symmetric corner scallops."""

import cadquery as cq

from ..common.die import finish_die
from ..common.geometry import corner_pocket_cube


def build() -> dict[str, cq.Shape]:
    return {"die": finish_die(corner_pocket_cube())}
