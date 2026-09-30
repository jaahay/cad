"""Rounded tactile die with shallow perimeter channels."""

import cadquery as cq

from ..common.die import finish_die
from ..common.geometry import edge_channel_cube


def build() -> dict[str, cq.Shape]:
    return {"die": finish_die(edge_channel_cube())}
