import json

import pytest

from tactile_dice.handoff import (
    BATCH_FORMAT,
    HANDOFF_FORMAT,
    BatchCandidate,
    DesignRef,
    candidate_label,
    copy_plate_stl,
    variation_specs,
    write_batch_summary,
    write_handoff_manifest,
)


BASELINE = DesignRef(
    body="mochi-soft",
    number_style="bubbles",
    shape_label="Mochi",
    number_label="Bubbles",
)


def test_candidate_labels_scale_beyond_one_letter() -> None:
    assert candidate_label(0) == "A"
    assert candidate_label(25) == "Z"
    assert candidate_label(26) == "AA"
    assert candidate_label(27) == "AB"
    with pytest.raises(ValueError):
        candidate_label(-1)


def test_variation_specs_are_baseline_first_and_change_one_axis() -> None:
    bodies = ("mochi-soft", "facet", "nested-steps")
    numbers = ("pips", "bubbles", "buttons")

    shape_variants = variation_specs(
        "mochi-soft",
        "bubbles",
        "shape",
        bodies,
        numbers,
    )
    assert shape_variants == (
        ("mochi-soft", "bubbles"),
        ("facet", "bubbles"),
        ("nested-steps", "bubbles"),
    )

    number_variants = variation_specs(
        "mochi-soft",
        "bubbles",
        "numbers",
        bodies,
        numbers,
    )
    assert number_variants == (
        ("mochi-soft", "bubbles"),
        ("mochi-soft", "pips"),
        ("mochi-soft", "buttons"),
    )


def test_single_handoff_manifest_is_neutral_and_points_at_exports(tmp_path) -> None:
    manifest_path = write_handoff_manifest(tmp_path, BASELINE)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["format"] == HANDOFF_FORMAT
    assert payload["design"]["body"] == "mochi-soft"
    assert payload["design"]["number_style"] == "bubbles"
    assert payload["files"] == {
        "stl": "stl/die.stl",
        "step": "step/die.step",
    }
    assert payload["manufacturing"]["handoff"] == "neutral"
    assert payload["manufacturing"]["slicer_project_generated"] is False
    assert ".3mf" not in manifest_path.read_text(encoding="utf-8")


def test_batch_summary_and_plate_copy_preserve_candidate_identity(tmp_path) -> None:
    handoff_dir = tmp_path / "candidates" / "A-mochi-soft--bubbles"
    source = handoff_dir / "stl" / "die.stl"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"fake-stl")

    plate_stl = copy_plate_stl(source, tmp_path / "plate", "A", BASELINE)
    candidate = BatchCandidate(
        label="A",
        design=BASELINE,
        handoff_dir="candidates/A-mochi-soft--bubbles",
        plate_stl=f"plate/{plate_stl.name}",
    )

    batch_path, readme_path = write_batch_summary(
        tmp_path,
        BASELINE,
        "shape",
        (candidate,),
    )
    payload = json.loads(batch_path.read_text(encoding="utf-8"))

    assert payload["format"] == BATCH_FORMAT
    assert payload["varied_axis"] == "shape"
    assert payload["candidates"][0]["label"] == "A"
    assert plate_stl.read_bytes() == b"fake-stl"
    assert "Mochi" in readme_path.read_text(encoding="utf-8")
    assert ".3mf" not in readme_path.read_text(encoding="utf-8")
