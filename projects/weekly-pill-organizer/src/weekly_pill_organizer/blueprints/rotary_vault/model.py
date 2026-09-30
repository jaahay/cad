"""Rotary Vault blueprint composition and invariants."""

from __future__ import annotations

import cadquery as cq

from .body import build_body
from .carousel import build_carousel
from .lid import build_lid
from .parameters import DAY_NAMES, INDEX_ANGLE, POSITION_COUNT
from .selector import build_selector


def validate_blueprint() -> None:
    if POSITION_COUNT != 8:
        raise ValueError("Rotary Vault requires exactly eight indexed positions")
    if len(DAY_NAMES) != POSITION_COUNT:
        raise ValueError("Day labels must match the eight indexed positions")
    if DAY_NAMES[0] != "CLOSED":
        raise ValueError("Position zero must be the solid CLOSED sector")
    if tuple(DAY_NAMES[1:]) != (
        "MON",
        "TUE",
        "WED",
        "THU",
        "FRI",
        "SAT",
        "SUN",
    ):
        raise ValueError("Positions 1-7 must be MON through SUN")
    if INDEX_ANGLE != 45.0:
        raise ValueError("Eight-position indexing must be exactly 45 degrees")


def build() -> dict[str, cq.Shape]:
    validate_blueprint()
    return {
        "body": build_body(),
        "carousel": build_carousel(),
        "lid": build_lid(),
        "selector": build_selector(),
    }
