"""Neutral print handoffs and one-trait prototype-batch metadata."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import random
import shutil

from .common.design import DesignSpec
from .common.parameters import SIZE
from .manufacturing import showcase_manifest


HANDOFF_FORMAT = "tactile-dice-handoff/v4"
BATCH_FORMAT = "tactile-dice-prototype-batch/v3"
TRAITS = ("shape", "numbers", "intensity")
TRAIT_LABELS = {
    "shape": "Shape",
    "numbers": "Number style",
    "intensity": "Tactile intensity",
}


@dataclass(frozen=True)
class DesignRef:
    spec: DesignSpec
    shape_label: str
    number_label: str
    intensity_label: str

    @property
    def slug(self) -> str:
        return self.spec.slug

    def as_dict(self) -> dict[str, str]:
        return {
            **self.spec.as_dict(),
            "shape_label": self.shape_label,
            "number_label": self.number_label,
            "intensity_label": self.intensity_label,
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


def resolve_trait(
    requested_trait: str,
    rng: random.Random | random.SystemRandom | None = None,
) -> str:
    """Resolve a concrete trait, including the playful surprise option."""
    if requested_trait in TRAITS:
        return requested_trait
    if requested_trait != "surprise":
        raise ValueError(f"unknown prototype-batch trait: {requested_trait}")

    chooser = rng or random.SystemRandom()
    return chooser.choice(TRAITS)


def variation_specs(
    baseline: DesignSpec,
    trait: str,
    bodies: tuple[str, ...],
    number_styles: tuple[str, ...],
    intensities: tuple[str, ...],
) -> tuple[DesignSpec, ...]:
    """Return baseline-first variants that change exactly one design trait."""
    if trait not in TRAITS:
        raise ValueError(f"unknown prototype-batch trait: {trait}")
    if baseline.body not in bodies:
        raise ValueError(f"unknown baseline body: {baseline.body}")
    if baseline.number_style not in number_styles:
        raise ValueError(
            f"unknown baseline number style: {baseline.number_style}"
        )
    if baseline.intensity not in intensities:
        raise ValueError(f"unknown baseline intensity: {baseline.intensity}")

    if trait == "shape":
        variants = tuple(
            DesignSpec(body, baseline.number_style, baseline.intensity)
            for body in bodies
            if body != baseline.body
        )
    elif trait == "numbers":
        variants = tuple(
            DesignSpec(baseline.body, number_style, baseline.intensity)
            for number_style in number_styles
            if number_style != baseline.number_style
        )
    else:
        variants = tuple(
            DesignSpec(baseline.body, baseline.number_style, intensity)
            for intensity in intensities
            if intensity != baseline.intensity
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
            "print_stl": "print/showcase.stl",
        },
        "manufacturing": {
            "nominal_body_size_mm": SIZE,
            "handoff": "neutral",
            "recommended_print_file": "print/showcase.stl",
            "showcase": showcase_manifest(),
            "post_processing": {
                "sanding": "none-by-default",
                "support_removal": (
                    "snap-or-cut breakaway rail; spot-deburr contacted edge only if needed"
                ),
                "painting": {
                    "optional": True,
                    "recommended_experiments": [
                        "unpainted",
                        "recessed-paint-fill",
                        "raised-detail-accent",
                    ],
                },
            },
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
    requested_trait: str,
    varied_trait: str,
    candidates: tuple[BatchCandidate, ...],
) -> tuple[Path, Path]:
    if requested_trait not in (*TRAITS, "surprise"):
        raise ValueError(f"unknown requested trait: {requested_trait}")
    if varied_trait not in TRAITS:
        raise ValueError(f"unknown varied trait: {varied_trait}")
    if requested_trait != "surprise" and requested_trait != varied_trait:
        raise ValueError("non-surprise batch must vary the requested trait")
    if not candidates:
        raise ValueError("prototype batch must contain at least one candidate")
    if candidates[0].design != baseline:
        raise ValueError("prototype batch must keep the baseline as candidate A")

    output.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": BATCH_FORMAT,
        "baseline": baseline.as_dict(),
        "requested_trait": requested_trait,
        "varied_trait": varied_trait,
        "candidates": [candidate.as_dict() for candidate in candidates],
    }

    manifest_path = output / "batch.json"
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Tactile Dice Prototype Batch",
        "",
        (
            "Baseline: "
            f"**{baseline.shape_label} + {baseline.number_label} + "
            f"{baseline.intensity_label}**"
        ),
        f"Varied trait: **{TRAIT_LABELS[varied_trait]}**",
    ]
    if requested_trait == "surprise":
        lines.append("Requested mode: **Surprise one trait**")

    lines.extend(
        [
            "",
            "Select all STL files in `plate/` and open or drag them into your slicer together.",
            "This is a neutral handoff; no slicer project file is generated.",
            "",
            "| Label | Shape | Numbers | Intensity | Plate STL |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for candidate in candidates:
        lines.append(
            "| "
            f"{candidate.label} | "
            f"{candidate.design.shape_label} | "
            f"{candidate.design.number_label} | "
            f"{candidate.design.intensity_label} | "
            f"`{candidate.plate_stl}` |"
        )

    readme_path = output / "README.md"
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path, readme_path
