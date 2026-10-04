"""Soft rounded tactile-die body blueprint."""

import cadquery as cq

from ..common.die import finish_die
from ..common.geometry import rounded_cube


def body() -> cq.Shape:
    return rounded_cube(3.8)


def build() -> dict[str, cq.Shape]:
    return {"die": finish_die(body())}
