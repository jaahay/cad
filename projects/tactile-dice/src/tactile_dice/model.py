"""Tactile-dice model definitions."""

import cadquery as cq

from .geometry import chamfered_cube, corner_pocket_cube, edge_channel_cube, pip_sphere, rounded_cube
from .parameters import FACE_VALUES, OPPOSITE_FACES, PIP_OFFSET, PIPS


def validate_definition() -> None:
    values = sorted(FACE_VALUES.values())
    if values != [1, 2, 3, 4, 5, 6]:
        raise ValueError(f"FACE_VALUES must contain 1 through 6 exactly once; got {values}")

    for value in range(1, 7):
        if len(PIPS[value]) != value:
            raise ValueError(f"Pip layout for {value} contains {len(PIPS[value])} marks")

    for first, second in OPPOSITE_FACES:
        if FACE_VALUES[first] + FACE_VALUES[second] != 7:
            raise ValueError(f"Opposite faces {first}/{second} do not sum to 7")


def add_face_pips(body: cq.Shape, face: str, value: int) -> cq.Shape:
    for horizontal, vertical in PIPS[value]:
        body = body.cut(pip_sphere(face, horizontal * PIP_OFFSET, vertical * PIP_OFFSET))
    return body


def finish_die(body: cq.Shape) -> cq.Shape:
    for face, value in FACE_VALUES.items():
        body = add_face_pips(body, face, value)
    return body


def build_all() -> dict[str, cq.Shape]:
    validate_definition()
    return {
        "mochi_soft": finish_die(rounded_cube(3.8)),
        "spherocube": finish_die(rounded_cube(5.8)),
        "facet": finish_die(chamfered_cube(2.4)),
        "edge_channel": finish_die(edge_channel_cube()),
        "corner_pocket": finish_die(corner_pocket_cube()),
    }
