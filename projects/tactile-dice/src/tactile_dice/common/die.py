"""Shared d6 semantics and tactile count finishing."""

import cadquery as cq

from .geometry import bubble_sphere, button_cylinder, pip_sphere
from .parameters import FACE_VALUES, OPPOSITE_FACES, PIP_OFFSET, PIPS


MARK_STYLES = ("pips", "bubbles", "buttons")


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


def validate_mark_style(mark_style: str) -> None:
    if mark_style not in MARK_STYLES:
        raise ValueError(
            f"Unknown tactile mark style {mark_style!r}; "
            f"choose from: {', '.join(MARK_STYLES)}"
        )


def add_face_marks(
    body: cq.Shape,
    face: str,
    value: int,
    mark_style: str,
) -> cq.Shape:
    for horizontal, vertical in PIPS[value]:
        u = horizontal * PIP_OFFSET
        v = vertical * PIP_OFFSET

        if mark_style == "pips":
            body = body.cut(pip_sphere(face, u, v))
        elif mark_style == "bubbles":
            body = body.fuse(bubble_sphere(face, u, v))
        elif mark_style == "buttons":
            body = body.fuse(button_cylinder(face, u, v))
        else:
            raise AssertionError(mark_style)

    return body


def finish_die(body: cq.Shape, mark_style: str = "pips") -> cq.Shape:
    validate_definition()
    validate_mark_style(mark_style)

    for face, value in FACE_VALUES.items():
        body = add_face_marks(body, face, value, mark_style)
    return body
