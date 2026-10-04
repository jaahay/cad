"""Rounded tactile-die body with symmetric corner scallops."""

import cadquery as cq

from ..common.die import finish_die
from ..common.geometry import corner_pocket_cube


def body() -> cq.Shape:
    return corner_pocket_cube()


def build() -> dict[str, cq.Shape]:
    return {"die": finish_die(body())}
