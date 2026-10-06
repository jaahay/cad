"""Coherent Tactile Dice design specification and tactile-intensity presets."""

from __future__ import annotations

from dataclasses import dataclass


INTENSITY_SCALES = {
    "gentle": 0.85,
    "standard": 1.0,
    "bold": 1.30,
}


@dataclass(frozen=True)
class DesignSpec:
    """The three traits that currently define one generated die."""

    body: str
    number_style: str
    intensity: str = "standard"

    @property
    def slug(self) -> str:
        return f"{self.body}--{self.number_style}--{self.intensity}"

    def as_dict(self) -> dict[str, str]:
        return {
            "body": self.body,
            "number_style": self.number_style,
            "intensity": self.intensity,
        }


def validate_intensity(intensity: str) -> None:
    if intensity not in INTENSITY_SCALES:
        raise ValueError(
            f"Unknown tactile intensity {intensity!r}; "
            f"choose from: {', '.join(INTENSITY_SCALES)}"
        )


def intensity_scale(intensity: str) -> float:
    validate_intensity(intensity)
    return INTENSITY_SCALES[intensity]
