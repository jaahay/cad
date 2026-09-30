import pytest

from tactile_dice.project import blueprints, build, validate_project
from tactile_dice.common.parameters import FACE_VALUES, OPPOSITE_FACES, PIPS, SIZE


EXPECTED_BLUEPRINTS = (
    "mochi-soft",
    "spherocube",
    "facet",
    "edge-channel",
    "corner-pocket",
)


def test_project_contract_and_standard_d6_definition() -> None:
    validate_project()
    assert blueprints() == EXPECTED_BLUEPRINTS
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
