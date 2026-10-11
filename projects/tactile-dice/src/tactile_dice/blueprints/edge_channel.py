"""Rounded tactile-die body with shallow perimeter channels."""

import cadquery as cq

from ..common.body import build_preset_body
from ..common.die import finish_die


def body() -> cq.Shape:
    return build_preset_body("edge-channel")


def build() -> dict[str, cq.Shape]:
    return {"die": finish_die(body())}
