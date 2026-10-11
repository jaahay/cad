from itertools import product

import pytest

from tactile_dice.common.body import BodySpec, PRESET_SPECS
from tactile_dice.common.design import INTENSITY_SCALES
from tactile_dice.common.parameters import FACE_VALUES, OPPOSITE_FACES, PIPS, SIZE
from tactile_dice.manufacturing import (
    build_showcase_print,
    canonical_one_two_edge_midpoint,
    rotate_showcase_point,
)
from tactile_dice.project import (
    base_options,
    blueprints,
    body_label,
    body_options,
    build,
    build_body,
    build_design,
    corner_options,
    edge_options,
    face_options,
    intensity_options,
    make_custom_body_slug,
    mark_options,
    public_custom_body_specs,
    validate_project,
)


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
    "paws",
)

EXPECTED_INTENSITIES = (
    "gentle",
    "standard",
    "bold",
)


def test_project_contract_and_standard_d6_definition() -> None:
    validate_project()
    assert blueprints() == EXPECTED_BLUEPRINTS
    assert tuple(slug for slug, _, _ in body_options()) == EXPECTED_BLUEPRINTS
    assert tuple(slug for slug, _, _ in mark_options()) == EXPECTED_MARK_STYLES
    assert tuple(slug for slug, _, _ in intensity_options()) == EXPECTED_INTENSITIES
    assert tuple(slug for slug, _, _ in base_options()) == (
        "balanced",
        "mochi",
        "spherocube",
        "faceted",
    )
    assert tuple(slug for slug, _, _ in edge_options()) == ("plain", "channels")
    assert tuple(slug for slug, _, _ in face_options()) == ("plain", "nested")
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
        "Paws",
    ]
    assert [label for _, label, _ in intensity_options()] == [
        "Gentle",
        "Standard",
        "Bold",
    ]
    assert INTENSITY_SCALES["standard"] == 1.0
    assert set(FACE_VALUES.values()) == set(range(1, 7))
    assert all(FACE_VALUES[a] + FACE_VALUES[b] == 7 for a, b in OPPOSITE_FACES)
    assert all(len(PIPS[value]) == value for value in range(1, 7))


def test_existing_named_bodies_are_presets_on_the_composable_engine() -> None:
    assert PRESET_SPECS == {
        "mochi-soft": BodySpec(base="mochi"),
        "spherocube": BodySpec(base="spherocube"),
        "facet": BodySpec(base="faceted"),
        "edge-channel": BodySpec(base="balanced", edge="channels"),
        "corner-pocket": BodySpec(base="_legacy-pocket", corner="pockets"),
        "nested-steps": BodySpec(base="balanced", face="nested"),
    }


def test_public_body_grammar_is_bounded_and_meaningful() -> None:
    specs = public_custom_body_specs()
    assert len(specs) == 24
    assert all(spec.base in {"balanced", "mochi", "spherocube", "faceted"} for spec in specs)
    assert all(
        not (spec.corner == "pockets" and spec.base in {"mochi", "spherocube"})
        for spec in specs
    )
    assert tuple(slug for slug, _, _ in corner_options("mochi")) == ("plain",)
    assert tuple(slug for slug, _, _ in corner_options("balanced")) == (
        "plain",
        "pockets",
    )


@pytest.mark.parametrize("spec", public_custom_body_specs())
def test_every_public_body_configuration_is_one_valid_nominal_solid(
    spec: BodySpec,
) -> None:
    body_name = make_custom_body_slug(
        spec.base,
        spec.edge,
        spec.corner,
        spec.face,
    )
    body = build_body(body_name)
    assert body.isValid()
    assert len(body.Solids()) == 1
    box = body.BoundingBox()
    assert box.xlen == pytest.approx(SIZE, abs=0.01)
    assert box.ylen == pytest.approx(SIZE, abs=0.01)
    assert box.zlen == pytest.approx(SIZE, abs=0.01)
    assert body_label(body_name)


def test_custom_body_composes_with_existing_number_and_intensity_system() -> None:
    body_name = make_custom_body_slug(
        "faceted",
        "channels",
        "pockets",
        "nested",
    )
    die = build_design(body_name, "paws", "bold")["die"]
    assert die.isValid()
    assert len(die.Solids()) == 1


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
    ("body_name", "mark_style", "intensity"),
    tuple(product(EXPECTED_BLUEPRINTS, EXPECTED_MARK_STYLES, EXPECTED_INTENSITIES)),
)
def test_every_body_mark_style_and_intensity_is_a_valid_single_die(
    body_name: str,
    mark_style: str,
    intensity: str,
) -> None:
    die = build_design(body_name, mark_style, intensity)["die"]
    assert die.isValid()
    assert len(die.Solids()) == 1

    box = die.BoundingBox()
    extents = (box.xlen, box.ylen, box.zlen)
    assert max(extents) - min(extents) < 0.05

    if mark_style == "pips":
        assert all(length == pytest.approx(SIZE, abs=0.01) for length in extents)
    else:
        assert all(SIZE < length < SIZE + 2.1 for length in extents)

    showcase = build_showcase_print(die)
    assert showcase.isValid()
    assert len(showcase.Solids()) == 1
    showcase_box = showcase.BoundingBox()
    assert showcase_box.zmin == pytest.approx(0.0, abs=0.01)
    assert showcase_box.zlen > SIZE


def test_showcase_rotation_puts_the_one_two_edge_down() -> None:
    edge = rotate_showcase_point(canonical_one_two_edge_midpoint())
    opposite_edge = rotate_showcase_point(
        tuple(-coordinate for coordinate in canonical_one_two_edge_midpoint())
    )

    assert edge[1] == pytest.approx(0.0, abs=1e-9)
    assert edge[2] < 0.0
    assert opposite_edge[1] == pytest.approx(0.0, abs=1e-9)
    assert opposite_edge[2] > 0.0


@pytest.mark.parametrize("mark_style", EXPECTED_MARK_STYLES)
def test_standard_intensity_remains_the_default_geometry(mark_style: str) -> None:
    default_die = build_design("mochi-soft", mark_style)["die"]
    standard_die = build_design("mochi-soft", mark_style, "standard")["die"]

    assert default_die.Volume() == pytest.approx(standard_die.Volume(), rel=1e-9)
    default_box = default_die.BoundingBox()
    standard_box = standard_die.BoundingBox()
    assert default_box.xlen == pytest.approx(standard_box.xlen, abs=1e-9)
    assert default_box.ylen == pytest.approx(standard_box.ylen, abs=1e-9)
    assert default_box.zlen == pytest.approx(standard_box.zlen, abs=1e-9)
