"""More spherical tactile-die body blueprint."""

import cadquery as cq

from ..common.body import build_preset_body
from ..common.die import finish_die


def body() -> cq.Shape:
    return build_preset_body("spherocube")


def build() -> dict[str, cq.Shape]:
    return {"die": finish_die(body())}
