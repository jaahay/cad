"""Shared d6 semantics and pip finishing."""

import cadquery as cq

from .geometry import pip_sphere
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
        body = body.cut(
            pip_sphere(face, horizontal * PIP_OFFSET, vertical * PIP_OFFSET)
        )
    return body


def finish_die(body: cq.Shape) -> cq.Shape:
    validate_definition()
    for face, value in FACE_VALUES.items():
        body = add_face_pips(body, face, value)
    return body
