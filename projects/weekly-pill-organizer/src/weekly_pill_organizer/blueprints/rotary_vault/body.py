"""Fixed lower shell and dispensing port for Rotary Vault."""

from __future__ import annotations

import math

import cadquery as cq

from .geometry import cylinder_x, cylinder_z, rounded_box, soft_oct_prism, sphere
from .parameters import (
    ACROSS_FLATS,
    BODY_H,
    BODY_KNUCKLE_LEN,
    CAROUSEL_R,
    CAROUSEL_Z,
    CLOSED_DETENT_R,
    CLOSED_EXTRA,
    CORNER_ROUND,
    DETENT_BALL_R,
    DETENT_LIFT,
    DETENT_R,
    HINGE_AXIS_Y,
    HINGE_AXIS_Z,
    HINGE_GAP,
    HINGE_PIN_D,
    HINGE_R,
    INNER_SHELL_R,
    LATCH_W,
    LID_KNUCKLE_LEN,
    PORT_CENTER_Y,
    PORT_DEPTH,
    PORT_H,
    PORT_W,
    PORT_Z0,
    selector_angle,
)


def _knuckle(x: float) -> cq.Shape:
    outer = cylinder_x(
        BODY_KNUCKLE_LEN, HINGE_R, (x, HINGE_AXIS_Y, HINGE_AXIS_Z)
    )
    bore = cylinder_x(
        BODY_KNUCKLE_LEN + 0.8,
        HINGE_PIN_D / 2.0,
        (x, HINGE_AXIS_Y, HINGE_AXIS_Z),
    )
    return outer.cut(bore)


def build_body() -> cq.Shape:
    body = soft_oct_prism(BODY_H, ACROSS_FLATS, CORNER_ROUND)

    well = cylinder_z(INNER_SHELL_R, BODY_H + 2.0, CAROUSEL_Z)
    body = body.cut(well)

    lip = cylinder_z(INNER_SHELL_R + 0.1, 1.4, CAROUSEL_Z).cut(
        cylinder_z(CAROUSEL_R - 0.25, 1.5, CAROUSEL_Z - 0.05)
    )
    body = body.fuse(lip)

    for sign in (-1.0, 1.0):
        x = sign * (
            LID_KNUCKLE_LEN / 2.0 + HINGE_GAP + BODY_KNUCKLE_LEN / 2.0
        )
        body = body.fuse(_knuckle(x))
        pedestal = (
            cq.Workplane("XY")
            .box(BODY_KNUCKLE_LEN, 5.0, 4.2)
            .val()
            .translate((x, ACROSS_FLATS / 2.0 + 0.7, BODY_H - 0.3))
        )
        body = body.fuse(pedestal)

    for index in range(8):
        angle = selector_angle(index)
        center = (
            DETENT_R * math.cos(math.radians(angle)),
            DETENT_R * math.sin(math.radians(angle)),
            CAROUSEL_Z + DETENT_LIFT - DETENT_BALL_R,
        )
        body = body.fuse(sphere(DETENT_BALL_R, center))

    closed_center = (
        0.0,
        -CLOSED_DETENT_R,
        CAROUSEL_Z + DETENT_LIFT + CLOSED_EXTRA - DETENT_BALL_R,
    )
    body = body.fuse(sphere(DETENT_BALL_R, closed_center))

    port_center = (0.0, PORT_CENTER_Y, PORT_Z0 + PORT_H / 2.0)
    body = body.cut(
        rounded_box((PORT_W, PORT_DEPTH, PORT_H), 2.2, port_center)
    )

    receiver = (
        cq.Workplane("XY")
        .box(LATCH_W + 1.0, 3.2, 1.8)
        .val()
        .translate((0.0, -ACROSS_FLATS / 2.0 + 0.5, BODY_H - 1.4))
    )
    body = body.cut(receiver)
    return body
