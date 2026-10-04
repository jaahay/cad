"""Crisp chamfered tactile-die body blueprint."""

import cadquery as cq

from ..common.die import finish_die
from ..common.geometry import chamfered_cube


def body() -> cq.Shape:
    return chamfered_cube(2.4)


def build() -> dict[str, cq.Shape]:
    return {"die": finish_die(body())}
