import pytest

from tactile_dice.model import build_all, validate_definition
from tactile_dice.parameters import FACE_VALUES, OPPOSITE_FACES, PIPS, SIZE


EXPECTED_MODELS = {
    "mochi_soft",
    "spherocube",
    "facet",
    "edge_channel",
    "corner_pocket",
}


def test_definition_is_standard_d6() -> None:
    validate_definition()
    assert set(FACE_VALUES.values()) == set(range(1, 7))
    assert all(FACE_VALUES[a] + FACE_VALUES[b] == 7 for a, b in OPPOSITE_FACES)
    assert all(len(PIPS[value]) == value for value in range(1, 7))


def test_all_expected_models_are_valid_single_solids() -> None:
    models = build_all()
    assert set(models) == EXPECTED_MODELS

    for model in models.values():
        assert model.isValid()
        assert len(model.Solids()) == 1


@pytest.mark.parametrize("name", sorted(EXPECTED_MODELS))
def test_models_keep_nominal_24_mm_envelope(name: str) -> None:
    model = build_all()[name]
    box = model.BoundingBox()
    assert box.xlen == pytest.approx(SIZE, abs=0.01)
    assert box.ylen == pytest.approx(SIZE, abs=0.01)
    assert box.zlen == pytest.approx(SIZE, abs=0.01)
