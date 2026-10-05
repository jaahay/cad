"""Neutral print handoffs and prototype-batch metadata for Tactile Dice."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil

from .common.parameters import SIZE


HANDOFF_FORMAT = "tactile-dice-handoff/v1"
BATCH_FORMAT = "tactile-dice-prototype-batch/v1"
VARIATION_AXES = ("shape", "numbers")


@dataclass(frozen=True)
class DesignRef:
    body: str
    number_style: str
    shape_label: str
    number_label: str

    @property
    def slug(self) -> str:
        return f"{self.body}--{self.number_style}"

    def as_dict(self) -> dict[str, str]:
        return {
            "body": self.body,
            "number_style": self.number_style,
            "shape_label": self.shape_label,
            "number_label": self.number_label,
        }


@dataclass(frozen=True)
class BatchCandidate:
    label: str
    design: DesignRef
    handoff_dir: str
    plate_stl: str

    def as_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "design": self.design.as_dict(),
            "handoff_dir": self.handoff_dir,
            "plate_stl": self.plate_stl,
        }


def candidate_label(index: int) -> str:
    """Return A..Z, AA..AZ, ... labels for zero-based candidate indices."""
    if index < 0:
        raise ValueError("candidate index must be non-negative")

    value = index + 1
    label = ""
    while value:
        value, remainder = divmod(value - 1, 26)
        label = chr(ord("A") + remainder) + label
    return label


def variation_specs(
    baseline_body: str,
    baseline_number_style: str,
    axis: str,
    bodies: tuple[str, ...],
    number_styles: tuple[str, ...],
) -> tuple[tuple[str, str], ...]:
    """Return baseline-first one-axis-at-a-time variants."""
    if axis not in VARIATION_AXES:
        raise ValueError(f"unknown variation axis: {axis}")
    if baseline_body not in bodies:
        raise ValueError(f"unknown baseline body: {baseline_body}")
    if baseline_number_style not in number_styles:
        raise ValueError(f"unknown baseline number style: {baseline_number_style}")

    baseline = (baseline_body, baseline_number_style)
    if axis == "shape":
        variants = tuple(
            (body, baseline_number_style)
            for body in bodies
            if body != baseline_body
        )
    else:
        variants = tuple(
            (baseline_body, number_style)
            for number_style in number_styles
            if number_style != baseline_number_style
        )

    return (baseline, *variants)


def write_handoff_manifest(output: Path, design: DesignRef) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": HANDOFF_FORMAT,
        "design": design.as_dict(),
        "files": {
            "stl": "stl/die.stl",
            "step": "step/die.step",
        },
        "manufacturing": {
            "nominal_body_size_mm": SIZE,
            "handoff": "neutral",
            "slicer_project_generated": False,
        },
    }

    path = output / "manifest.json"
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def copy_plate_stl(
    source: Path,
    plate_dir: Path,
    label: str,
    design: DesignRef,
) -> Path:
    if not source.is_file():
        raise FileNotFoundError(source)

    plate_dir.mkdir(parents=True, exist_ok=True)
    target = plate_dir / f"{label}-{design.slug}.stl"
    shutil.copy2(source, target)
    return target


def write_batch_summary(
    output: Path,
    baseline: DesignRef,
    varied_axis: str,
    candidates: tuple[BatchCandidate, ...],
) -> tuple[Path, Path]:
    if varied_axis not in VARIATION_AXES:
        raise ValueError(f"unknown variation axis: {varied_axis}")
    if not candidates:
        raise ValueError("prototype batch must contain at least one candidate")
    if candidates[0].design != baseline:
        raise ValueError("prototype batch must keep the baseline as candidate A")

    output.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": BATCH_FORMAT,
        "baseline": baseline.as_dict(),
        "varied_axis": varied_axis,
        "candidates": [candidate.as_dict() for candidate in candidates],
    }

    manifest_path = output / "batch.json"
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    axis_label = "Shape" if varied_axis == "shape" else "Number style"
    lines = [
        "# Tactile Dice Prototype Batch",
        "",
        f"Baseline: **{baseline.shape_label} + {baseline.number_label}**",
        f"Varied axis: **{axis_label}**",
        "",
        "Select all STL files in `plate/` and open or drag them into your slicer together.",
        "This is a neutral handoff; no slicer project file is generated.",
        "",
        "| Label | Shape | Numbers | Plate STL |",
        "| --- | --- | --- | --- |",
    ]
    for candidate in candidates:
        lines.append(
            "| "
            f"{candidate.label} | "
            f"{candidate.design.shape_label} | "
            f"{candidate.design.number_label} | "
            f"`{candidate.plate_stl}` |"
        )

    readme_path = output / "README.md"
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path, readme_path
