"""Rotary 7-day + CLOSED carousel."""

from __future__ import annotations

import math

import cadquery as cq

from .geometry import cylinder_z, d_prism, sloped_sector_void, sphere
from .parameters import (
    CAROUSEL_H,
    CAROUSEL_R,
    CAVITY_R0,
    CAVITY_R1,
    CLOSED_DETENT_R,
    DETENT_BALL_R,
    DETENT_R,
    DRIVE_LEN,
    D_FLAT,
    FLOOR_INNER,
    FLOOR_OUTER,
    HUB_R,
    OUTLET_H,
    OUTLET_W,
    SECTOR_GAP_DEG,
    STEM_D,
    sector_angle,
)


def _outlet_void(index: int) -> cq.Shape:
    angle = sector_angle(index)
    radial = CAROUSEL_R + 1.0
    center = (
        radial * math.cos(math.radians(angle)),
        radial * math.sin(math.radians(angle)),
        FLOOR_OUTER + OUTLET_H / 2.0,
    )
    tunnel = cq.Workplane("XY").box(8.0, OUTLET_W, OUTLET_H).val()
    tunnel = tunnel.rotate((0, 0, 0), (0, 0, 1), angle)
    return tunnel.translate(center)


def build_carousel() -> cq.Shape:
    body = cylinder_z(CAROUSEL_R, CAROUSEL_H)
    body = body.fuse(cylinder_z(HUB_R + 1.8, CAROUSEL_H + 0.2))

    half_angle = 22.5 - SECTOR_GAP_DEG
    for index in range(1, 8):
        body = body.cut(
            sloped_sector_void(
                CAVITY_R0,
                CAVITY_R1,
                sector_angle(index),
                half_angle,
                FLOOR_INNER,
                FLOOR_OUTER,
                CAROUSEL_H + 0.8,
            )
        )
        body = body.cut(_outlet_void(index))

    # Keyed selector socket, deliberately stopped above the floor.
    socket_z = CAROUSEL_H - DRIVE_LEN + 0.2
    body = body.cut(d_prism(DRIVE_LEN + 0.8, STEM_D + 0.55, D_FLAT + 0.15, socket_z))

    # Underside detent pockets.
    for index in range(8):
        angle = sector_angle(index)
        center = (
            DETENT_R * math.cos(math.radians(angle)),
            DETENT_R * math.sin(math.radians(angle)),
            -DETENT_BALL_R + 0.40,
        )
        body = body.cut(sphere(DETENT_BALL_R + 0.12, center))

    # Unique deeper CLOSED keeper pocket at the front position.
    angle = sector_angle(0)
    center = (
        CLOSED_DETENT_R * math.cos(math.radians(angle)),
        CLOSED_DETENT_R * math.sin(math.radians(angle)),
        -DETENT_BALL_R + 0.58,
    )
    body = body.cut(sphere(DETENT_BALL_R + 0.18, center))
    return body
