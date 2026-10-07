import json
import random

import pytest

from tactile_dice.common.design import DesignSpec
from tactile_dice.handoff import (
    BATCH_FORMAT,
    HANDOFF_FORMAT,
    TRAITS,
    BatchCandidate,
    DesignRef,
    candidate_label,
    copy_plate_stl,
    resolve_trait,
    variation_specs,
    write_batch_summary,
    write_handoff_manifest,
)


BASELINE = DesignRef(
    spec=DesignSpec("mochi-soft", "bubbles", "standard"),
    shape_label="Mochi",
    number_label="Bubbles",
    intensity_label="Standard",
)


def test_candidate_labels_scale_beyond_one_letter() -> None:
    assert candidate_label(0) == "A"
    assert candidate_label(25) == "Z"
    assert candidate_label(26) == "AA"
    assert candidate_label(27) == "AB"
    with pytest.raises(ValueError):
        candidate_label(-1)


def test_variation_specs_are_baseline_first_and_change_one_trait() -> None:
    bodies = ("mochi-soft", "facet", "nested-steps")
    numbers = ("pips", "bubbles", "buttons")
    intensities = ("gentle", "standard", "bold")

    shape_variants = variation_specs(
        BASELINE.spec, "shape", bodies, numbers, intensities
    )
    assert shape_variants == (
        DesignSpec("mochi-soft", "bubbles", "standard"),
        DesignSpec("facet", "bubbles", "standard"),
        DesignSpec("nested-steps", "bubbles", "standard"),
    )

    number_variants = variation_specs(
        BASELINE.spec, "numbers", bodies, numbers, intensities
    )
    assert number_variants == (
        DesignSpec("mochi-soft", "bubbles", "standard"),
        DesignSpec("mochi-soft", "pips", "standard"),
        DesignSpec("mochi-soft", "buttons", "standard"),
    )

    intensity_variants = variation_specs(
        BASELINE.spec, "intensity", bodies, numbers, intensities
    )
    assert intensity_variants == (
        DesignSpec("mochi-soft", "bubbles", "standard"),
        DesignSpec("mochi-soft", "bubbles", "gentle"),
        DesignSpec("mochi-soft", "bubbles", "bold"),
    )


def test_surprise_trait_can_be_reproduced_with_a_seeded_rng() -> None:
    first = resolve_trait("surprise", random.Random(27))
    second = resolve_trait("surprise", random.Random(27))

    assert first == second
    assert first in TRAITS


def test_single_handoff_manifest_records_intensity_and_is_neutral(tmp_path) -> None:
    manifest_path = write_handoff_manifest(tmp_path, BASELINE)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["format"] == HANDOFF_FORMAT
    assert payload["design"]["body"] == "mochi-soft"
    assert payload["design"]["number_style"] == "bubbles"
    assert payload["design"]["intensity"] == "standard"
    assert payload["files"] == {
        "stl": "stl/die.stl",
        "step": "step/die.step",
        "print_stl": "print/showcase.stl",
    }
    assert payload["manufacturing"]["handoff"] == "neutral"
    assert payload["manufacturing"]["recommended_print_file"] == "print/showcase.stl"
    assert payload["manufacturing"]["showcase"]["downward_edge"] == [1, 2]
    assert (
        payload["manufacturing"]["showcase"]["support"]["kind"]
        == "integrated-breakaway-rail"
    )
    assert payload["manufacturing"]["slicer_project_generated"] is False
    assert ".3mf" not in manifest_path.read_text(encoding="utf-8")


def test_batch_summary_and_plate_copy_preserve_candidate_identity(tmp_path) -> None:
    handoff_dir = tmp_path / "candidates" / f"A-{BASELINE.slug}"
    source = handoff_dir / "stl" / "die.stl"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"fake-stl")

    plate_stl = copy_plate_stl(source, tmp_path / "plate", "A", BASELINE)
    candidate = BatchCandidate(
        label="A",
        design=BASELINE,
        handoff_dir=f"candidates/A-{BASELINE.slug}",
        plate_stl=f"plate/{plate_stl.name}",
    )

    batch_path, readme_path = write_batch_summary(
        tmp_path,
        BASELINE,
        "surprise",
        "intensity",
        (candidate,),
    )
    payload = json.loads(batch_path.read_text(encoding="utf-8"))

    assert payload["format"] == BATCH_FORMAT
    assert payload["requested_trait"] == "surprise"
    assert payload["varied_trait"] == "intensity"
    assert payload["candidates"][0]["label"] == "A"
    assert payload["candidates"][0]["design"]["intensity"] == "standard"
    assert plate_stl.read_bytes() == b"fake-stl"
    readme = readme_path.read_text(encoding="utf-8")
    assert "Tactile intensity" in readme
    assert "Surprise one trait" in readme
    assert ".3mf" not in readme
