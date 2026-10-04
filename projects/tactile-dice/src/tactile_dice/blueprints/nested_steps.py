"""Tactile-die body with two shallow inset face levels."""

import cadquery as cq

from ..common.die import finish_die
from ..common.geometry import nested_steps_cube


def body() -> cq.Shape:
    return nested_steps_cube()


def build() -> dict[str, cq.Shape]:
    return {"die": finish_die(body())}
