import math

import pytest

from rotary_vault.model import build_all, validate_definition
from rotary_vault.parameters import (
    ACROSS_FLATS,
    CAROUSEL_H,
    CAROUSEL_R,
    CAROUSEL_CLEARANCE,
    DAY_NAMES,
    INDEX_ANGLE,
    INNER_SHELL_R,
    OUTLET_W,
    PORT_W,
    POSITION_COUNT,
    CAROUSEL_Z,
    sector_angle,
)


def test_indexing_contract() -> None:
    validate_definition()
    assert POSITION_COUNT == 8
    assert INDEX_ANGLE == 45.0
    assert DAY_NAMES == ("CLOSED", "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")


def test_all_production_parts_are_valid_single_solids() -> None:
    models = build_all()
    assert set(models) == {"body", "carousel", "lid", "selector"}
    for name, model in models.items():
        assert model.isValid(), name
        assert len(model.Solids()) == 1, name


def test_carousel_keeps_expected_envelope() -> None:
    carousel = build_all()["carousel"]
    box = carousel.BoundingBox()
    assert box.xlen == pytest.approx(2.0 * CAROUSEL_R, abs=0.05)
    assert box.ylen == pytest.approx(2.0 * CAROUSEL_R, abs=0.05)
    assert box.zlen == pytest.approx(CAROUSEL_H, abs=0.25)


def test_body_keeps_soft_octagonal_core_envelope() -> None:
    body = build_all()["body"]
    box = body.BoundingBox()
    # Hinge hardware extends beyond the shell in +Y; X should retain the 92 mm shell width.
    assert box.xlen == pytest.approx(ACROSS_FLATS, abs=0.2)


def test_closed_sector_is_material_at_front() -> None:
    carousel = build_all()["carousel"]
    # Probe a point well inside the CLOSED front wedge and above its floor.
    assert carousel.isInside((0.0, -30.0, 8.0))


@pytest.mark.parametrize("index", range(1, 8))
def test_each_day_sector_is_hollow(index: int) -> None:
    carousel = build_all()["carousel"]
    angle = math.radians(sector_angle(index))
    point = (30.0 * math.cos(angle), 30.0 * math.sin(angle), 8.0)
    assert not carousel.isInside(point)


def test_carousel_clearance_and_port_width_are_explicit() -> None:
    assert INNER_SHELL_R - CAROUSEL_R == pytest.approx(CAROUSEL_CLEARANCE)
    assert PORT_W > OUTLET_W


def test_fixed_port_breaks_completely_through_shell() -> None:
    body = build_all()["body"]
    # This point lies in the front shell wall between the carousel well and exterior.
    assert not body.isInside((0.0, -40.5, 8.0))


def test_closed_and_monday_states_differ_at_fixed_port() -> None:
    models = build_all()
    body = models["body"]
    carousel = models["carousel"].translate((0.0, 0.0, CAROUSEL_Z))
    probe = (0.0, -38.5, 8.0)

    # The shell itself is open at the port; CLOSED is blocked by the solid carousel sector.
    assert not body.isInside(probe)
    assert carousel.isInside(probe)

    monday = carousel.rotate((0, 0, 0), (0, 0, 1), -45.0)
    assert not monday.isInside(probe)
