"""Canonical dimensions and indexing for the Rotary Vault prototype."""

from __future__ import annotations

import math

DAY_NAMES = ("CLOSED", "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
POSITION_COUNT = 8
INDEX_ANGLE = 360.0 / POSITION_COUNT
FRONT_ANGLE = -90.0

# Envelope
ACROSS_FLATS = 92.0
CORNER_ROUND = 6.0
BODY_H = 18.6
LID_T = 3.0
CAROUSEL_Z = 2.3

# Carousel / shell fit
CAROUSEL_H = 15.2
CAROUSEL_R = 39.0
CAROUSEL_CLEARANCE = 0.42
INNER_SHELL_R = CAROUSEL_R + CAROUSEL_CLEARANCE
HUB_R = 8.5
SECTOR_GAP_DEG = 2.0
CAVITY_R0 = 11.0
CAVITY_R1 = 37.3
FLOOR_OUTER = 1.5
FLOOR_INNER = 4.5
OUTLET_W = 20.0
OUTLET_H = 12.0

# Fixed dispensing port
PORT_W = 24.5
PORT_H = 12.5
PORT_Z0 = 2.8
PORT_DEPTH = 18.0
PORT_CENTER_Y = -ACROSS_FLATS / 2.0 + 2.0

# Selector / drive
SELECTOR_D = 29.0
SELECTOR_H = 4.2
STEM_D = 8.2
STEM_LEN = 4.1
DRIVE_LEN = 4.8
D_FLAT = 2.1
SELECTOR_HOLE_D = 8.8
SELECTOR_BEAD_D = 9.4
SELECTOR_BEAD_H = 0.55

# Refill lid hinge
HINGE_AXIS_Y = ACROSS_FLATS / 2.0 + 3.1
HINGE_AXIS_Z = BODY_H + 0.6
HINGE_R = 2.4
HINGE_PIN_D = 2.15
BODY_KNUCKLE_LEN = 9.0
LID_KNUCKLE_LEN = 18.0
HINGE_GAP = 1.0

# Detents
DETENT_R = 27.0
DETENT_BALL_R = 1.35
DETENT_LIFT = 0.45
CLOSED_DETENT_R = 32.0
CLOSED_EXTRA = 0.20

# Weekly refill latch
LATCH_W = 13.0
LATCH_T = 1.4
LATCH_H = 4.2
LATCH_HOOK = 0.75

# Sampling resolution for CAD arcs. This affects source geometry rather than STL tessellation.
ARC_SEGMENTS = 24


def sector_angle(index: int) -> float:
    return FRONT_ANGLE + index * INDEX_ANGLE


def selector_angle(index: int) -> float:
    return FRONT_ANGLE - index * INDEX_ANGLE


def regular_octagon_circumradius(across_flats: float = ACROSS_FLATS) -> float:
    return across_flats / (2.0 * math.cos(math.radians(22.5)))
