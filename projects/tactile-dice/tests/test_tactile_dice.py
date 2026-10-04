from itertools import product

import pytest

from tactile_dice.project import (
    blueprints,
    body_options,
    build,
    build_design,
    mark_options,
    validate_project,
)
from tactile_dice.common.parameters import FACE_VALUES, OPPOSITE_FACES, PIPS, SIZE


EXPECTED_BLUEPRINTS = (
    "mochi-soft",
    "spherocube",
    "facet",
    "edge-channel",
    "corner-pocket",
    "nested-steps",
)

EXPECTED_MARK_STYLES = (
    "pips",
    "bubbles",
    "buttons",
)


def test_project_contract_and_standard_d6_definition() -> None:
    validate_project()
    assert blueprints() == EXPECTED_BLUEPRINTS
    assert tuple(slug for slug, _, _ in body_options()) == EXPECTED_BLUEPRINTS
    assert tuple(slug for slug, _, _ in mark_options()) == EXPECTED_MARK_STYLES
    assert [label for _, label, _ in body_options()] == [
        "Mochi",
        "Spherocube",
        "Faceted",
        "Edge Channels",
        "Corner Pockets",
        "Nested Steps",
    ]
    assert [label for _, label, _ in mark_options()] == [
        "Recessed pips",
        "Bubbles",
        "Buttons",
    ]
    assert set(FACE_VALUES.values()) == set(range(1, 7))
    assert all(FACE_VALUES[a] + FACE_VALUES[b] == 7 for a, b in OPPOSITE_FACES)
    assert all(len(PIPS[value]) == value for value in range(1, 7))


@pytest.mark.parametrize("blueprint", EXPECTED_BLUEPRINTS)
def test_blueprints_build_one_valid_24_mm_die(blueprint: str) -> None:
    parts = build(blueprint)
    assert set(parts) == {"die"}

    die = parts["die"]
    assert die.isValid()
    assert len(die.Solids()) == 1

    box = die.BoundingBox()
    assert box.xlen == pytest.approx(SIZE, abs=0.01)
    assert box.ylen == pytest.approx(SIZE, abs=0.01)
    assert box.zlen == pytest.approx(SIZE, abs=0.01)


@pytest.mark.parametrize(
    ("body_name", "mark_style"),
    tuple(product(EXPECTED_BLUEPRINTS, EXPECTED_MARK_STYLES)),
)
def test_every_body_and_mark_style_combination_is_a_valid_single_die(
    body_name: str,
    mark_style: str,
) -> None:
    die = build_design(body_name, mark_style)["die"]
    assert die.isValid()
    assert len(die.Solids()) == 1

    box = die.BoundingBox()
    extents = (box.xlen, box.ylen, box.zlen)
    assert max(extents) - min(extents) < 0.05

    if mark_style == "pips":
        assert all(length == pytest.approx(SIZE, abs=0.01) for length in extents)
    else:
        assert all(SIZE < length < SIZE + 2.0 for length in extents)
