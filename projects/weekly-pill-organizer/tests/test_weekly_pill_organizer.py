import math

import pytest

from weekly_pill_organizer.project import blueprints, build, validate_project
from weekly_pill_organizer.blueprints.rotary_vault.parameters import (
    ACROSS_FLATS,
    CAROUSEL_CLEARANCE,
    CAROUSEL_H,
    CAROUSEL_R,
    CAROUSEL_Z,
    DAY_NAMES,
    INDEX_ANGLE,
    INNER_SHELL_R,
    OUTLET_W,
    PORT_W,
    POSITION_COUNT,
    sector_angle,
)


def rotary_vault():
    return build("rotary-vault")


def test_project_contract() -> None:
    validate_project()
    assert blueprints() == ("rotary-vault",)


def test_rotary_vault_indexing_contract() -> None:
    assert POSITION_COUNT == 8
    assert INDEX_ANGLE == 45.0
    assert DAY_NAMES == (
        "CLOSED",
        "MON",
        "TUE",
        "WED",
        "THU",
        "FRI",
        "SAT",
        "SUN",
    )


def test_all_rotary_vault_parts_are_valid_single_solids() -> None:
    models = rotary_vault()
    assert set(models) == {"body", "carousel", "lid", "selector"}
    for name, model in models.items():
        assert model.isValid(), name
        assert len(model.Solids()) == 1, name


def test_carousel_keeps_expected_envelope() -> None:
    carousel = rotary_vault()["carousel"]
    box = carousel.BoundingBox()
    assert box.xlen == pytest.approx(2.0 * CAROUSEL_R, abs=0.05)
    assert box.ylen == pytest.approx(2.0 * CAROUSEL_R, abs=0.05)
    assert box.zlen == pytest.approx(CAROUSEL_H, abs=0.25)


def test_body_keeps_soft_octagonal_core_envelope() -> None:
    body = rotary_vault()["body"]
    box = body.BoundingBox()
    assert box.xlen == pytest.approx(ACROSS_FLATS, abs=0.2)


def test_closed_sector_is_material_at_front() -> None:
    carousel = rotary_vault()["carousel"]
    assert carousel.isInside((0.0, -30.0, 8.0))


@pytest.mark.parametrize("index", range(1, 8))
def test_each_day_sector_is_hollow(index: int) -> None:
    carousel = rotary_vault()["carousel"]
    angle = math.radians(sector_angle(index))
    point = (30.0 * math.cos(angle), 30.0 * math.sin(angle), 8.0)
    assert not carousel.isInside(point)


def test_carousel_clearance_and_port_width_are_explicit() -> None:
    assert INNER_SHELL_R - CAROUSEL_R == pytest.approx(CAROUSEL_CLEARANCE)
    assert PORT_W > OUTLET_W


def test_fixed_port_breaks_completely_through_shell() -> None:
    body = rotary_vault()["body"]
    assert not body.isInside((0.0, -40.5, 8.0))


def test_closed_and_monday_states_differ_at_fixed_port() -> None:
    models = rotary_vault()
    body = models["body"]
    carousel = models["carousel"].translate((0.0, 0.0, CAROUSEL_Z))
    probe = (0.0, -38.5, 8.0)

    assert not body.isInside(probe)
    assert carousel.isInside(probe)

    monday = carousel.rotate((0, 0, 0), (0, 0, 1), -45.0)
    assert not monday.isInside(probe)
