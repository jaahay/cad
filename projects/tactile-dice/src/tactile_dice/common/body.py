"""Composable tactile-die body grammar.

Public choices stay semantic. CAD-facing dimensions remain internal here and
in the shared geometry primitives.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import cadquery as cq

from .geometry import (
    apply_corner_pockets,
    apply_edge_channels,
    apply_nested_steps,
    chamfered_cube,
    rounded_cube,
)


BASE_OPTIONS = {
    "balanced": ("Balanced", "Classic rounded foundation."),
    "mochi": ("Mochi", "Soft rounded foundation."),
    "spherocube": ("Spherocube", "Very round foundation."),
    "faceted": ("Faceted", "Crisp chamfered foundation."),
}

EDGE_OPTIONS = {
    "plain": ("Plain", "No added edge treatment."),
    "channels": ("Channels", "Shallow perimeter grooves."),
}

CORNER_OPTIONS = {
    "plain": ("Plain", "Keep the base corners."),
    "pockets": ("Pockets", "Scooped corner accents."),
}

FACE_OPTIONS = {
    "plain": ("Plain", "Keep the base faces."),
    "nested": ("Nested Steps", "Two shallow inset face levels."),
}

# Hidden implementation profiles. These are intentionally not CLI controls.
_BASE_BUILDERS = {
    "balanced": ("rounded", 3.0),
    "mochi": ("rounded", 3.8),
    "spherocube": ("rounded", 5.8),
    "faceted": ("chamfered", 2.4),
    # The original Corner Pockets body used a slightly different rounding
    # radius. Keep that exact legacy geometry as a preset without exposing the
    # raw value as a user-facing choice.
    "_legacy-pocket": ("rounded", 3.2),
}


@dataclass(frozen=True)
class BodySpec:
    """One composable body before number marks are applied."""

    base: str = "balanced"
    edge: str = "plain"
    corner: str = "plain"
    face: str = "plain"

    @property
    def slug(self) -> str:
        return f"custom--{self.base}--{self.edge}--{self.corner}--{self.face}"

    def as_dict(self) -> dict[str, str]:
        return {
            "base": self.base,
            "edge": self.edge,
            "corner": self.corner,
            "face": self.face,
        }


PRESET_SPECS = {
    "mochi-soft": BodySpec(base="mochi"),
    "spherocube": BodySpec(base="spherocube"),
    "facet": BodySpec(base="faceted"),
    "edge-channel": BodySpec(base="balanced", edge="channels"),
    "corner-pocket": BodySpec(base="_legacy-pocket", corner="pockets"),
    "nested-steps": BodySpec(base="balanced", face="nested"),
}


def validate_body_spec(spec: BodySpec, *, public: bool = False) -> None:
    if spec.base not in _BASE_BUILDERS:
        raise ValueError(f"Unknown base character: {spec.base}")
    if spec.edge not in EDGE_OPTIONS:
        raise ValueError(f"Unknown edge treatment: {spec.edge}")
    if spec.corner not in CORNER_OPTIONS:
        raise ValueError(f"Unknown corner treatment: {spec.corner}")
    if spec.face not in FACE_OPTIONS:
        raise ValueError(f"Unknown face treatment: {spec.face}")

    if public:
        if spec.base not in BASE_OPTIONS:
            raise ValueError(f"Base character is not public: {spec.base}")
        # Deeply rounded bodies already remove most corner material. Hiding
        # pockets there avoids combinations that would be visually negligible.
        if spec.corner == "pockets" and spec.base in {"mochi", "spherocube"}:
            raise ValueError(
                f"{spec.base} is too rounded for a meaningful pocket treatment"
            )


def is_public_body_spec(spec: BodySpec) -> bool:
    try:
        validate_body_spec(spec, public=True)
    except ValueError:
        return False
    return True


def public_body_specs() -> tuple[BodySpec, ...]:
    candidates = (
        BodySpec(base, edge, corner, face)
        for base, edge, corner, face in product(
            BASE_OPTIONS,
            EDGE_OPTIONS,
            CORNER_OPTIONS,
            FACE_OPTIONS,
        )
    )
    return tuple(spec for spec in candidates if is_public_body_spec(spec))


def custom_body_slug(
    base: str,
    edge: str = "plain",
    corner: str = "plain",
    face: str = "plain",
) -> str:
    spec = BodySpec(base, edge, corner, face)
    validate_body_spec(spec, public=True)
    return spec.slug


def parse_custom_body_slug(slug: str) -> BodySpec:
    parts = slug.split("--")
    if len(parts) != 5 or parts[0] != "custom":
        raise ValueError(f"Not a custom tactile-dice body slug: {slug}")
    spec = BodySpec(parts[1], parts[2], parts[3], parts[4])
    validate_body_spec(spec, public=True)
    return spec


def resolve_body_spec(body_name: str) -> BodySpec:
    if body_name in PRESET_SPECS:
        spec = PRESET_SPECS[body_name]
        validate_body_spec(spec)
        return spec
    return parse_custom_body_slug(body_name)


def build_body_spec(spec: BodySpec) -> cq.Shape:
    validate_body_spec(spec)
    kind, value = _BASE_BUILDERS[spec.base]
    if kind == "rounded":
        body = rounded_cube(value)
    elif kind == "chamfered":
        body = chamfered_cube(value)
    else:
        raise AssertionError(kind)

    if spec.edge == "channels":
        body = apply_edge_channels(body)
    if spec.corner == "pockets":
        body = apply_corner_pockets(body)
    if spec.face == "nested":
        body = apply_nested_steps(body)

    if not body.isValid() or len(body.Solids()) != 1:
        raise ValueError(f"Body specification did not produce one valid solid: {spec}")
    return body


def build_preset_body(preset: str) -> cq.Shape:
    try:
        spec = PRESET_SPECS[preset]
    except KeyError as exc:
        raise ValueError(f"Unknown tactile-dice preset: {preset}") from exc
    return build_body_spec(spec)


def body_spec_label(spec: BodySpec) -> str:
    validate_body_spec(spec)
    base_label = (
        BASE_OPTIONS[spec.base][0]
        if spec.base in BASE_OPTIONS
        else "Balanced"
    )
    labels = [base_label]
    if spec.edge != "plain":
        labels.append(EDGE_OPTIONS[spec.edge][0])
    if spec.corner != "plain":
        labels.append(CORNER_OPTIONS[spec.corner][0])
    if spec.face != "plain":
        labels.append(FACE_OPTIONS[spec.face][0])
    return " + ".join(labels)
