"""Repository-facing contract for the Tactile Dice project."""

from __future__ import annotations

from importlib import import_module

import cadquery as cq

from .common.design import DesignSpec, INTENSITY_SCALES, validate_intensity
from .common.die import MARK_STYLES, finish_die, validate_definition


BODY_OPTIONS = {
    "mochi-soft": ("Mochi", "Soft and rounded."),
    "spherocube": ("Spherocube", "Very round and smooth."),
    "facet": ("Faceted", "Crisp angled edges."),
    "edge-channel": ("Edge Channels", "Grooves around the edges."),
    "corner-pocket": ("Corner Pockets", "Scooped corners."),
    "nested-steps": ("Nested Steps", "Layered tactile faces."),
}

MARK_OPTIONS = {
    "pips": ("Recessed pips", "Classic dice."),
    "bubbles": ("Bubbles", "Smooth raised bumps."),
    "buttons": ("Buttons", "Broad flat bumps."),
    "paws": ("Paws", "Chunky raised paw prints."),
}

INTENSITY_OPTIONS = {
    "gentle": ("Gentle", "Low-profile tactile marks."),
    "standard": ("Standard", "The familiar default feel."),
    "bold": ("Bold", "Extra-pronounced tactile marks."),
}

BLUEPRINT_MODULES = {
    "mochi-soft": "tactile_dice.blueprints.mochi",
    "spherocube": "tactile_dice.blueprints.spherocube",
    "facet": "tactile_dice.blueprints.facet",
    "edge-channel": "tactile_dice.blueprints.edge_channel",
    "corner-pocket": "tactile_dice.blueprints.corner_pocket",
    "nested-steps": "tactile_dice.blueprints.nested_steps",
}


def blueprints() -> tuple[str, ...]:
    return tuple(BLUEPRINT_MODULES)


def body_options() -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (slug, label, description)
        for slug, (label, description) in BODY_OPTIONS.items()
    )


def mark_options() -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (slug, label, description)
        for slug, (label, description) in MARK_OPTIONS.items()
    )


def intensity_options() -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (slug, label, description)
        for slug, (label, description) in INTENSITY_OPTIONS.items()
    )


def validate_project() -> None:
    validate_definition()
    if tuple(MARK_OPTIONS) != MARK_STYLES:
        raise ValueError(
            "Tactile Dice number-style metadata must match supported mark styles"
        )
    if tuple(INTENSITY_OPTIONS) != tuple(INTENSITY_SCALES):
        raise ValueError(
            "Tactile Dice intensity metadata must match supported intensity presets"
        )
    if tuple(BODY_OPTIONS) != blueprints():
        raise ValueError("Tactile Dice shape metadata must match blueprints")


def build_body(body_name: str) -> cq.Shape:
    validate_project()
    try:
        module_name = BLUEPRINT_MODULES[body_name]
    except KeyError as exc:
        raise ValueError(f"Unknown tactile-dice body: {body_name}") from exc

    module = import_module(module_name)
    body_builder = getattr(module, "body", None)
    if not callable(body_builder):
        raise TypeError(f"{body_name}: body blueprint must expose body()")
    return body_builder()


def build_design_spec(spec: DesignSpec) -> dict[str, cq.Shape]:
    validate_project()
    if spec.body not in BODY_OPTIONS:
        raise ValueError(f"Unknown tactile-dice body: {spec.body}")
    if spec.number_style not in MARK_OPTIONS:
        raise ValueError(f"Unknown tactile-dice mark style: {spec.number_style}")
    validate_intensity(spec.intensity)
    return {
        "die": finish_die(
            build_body(spec.body),
            spec.number_style,
            spec.intensity,
        )
    }


def build_design(
    body_name: str,
    mark_style: str,
    intensity: str = "standard",
) -> dict[str, cq.Shape]:
    return build_design_spec(DesignSpec(body_name, mark_style, intensity))


def build(blueprint: str) -> dict[str, cq.Shape]:
    """Repository blueprint builds use classic recessed pips at Standard intensity."""
    return build_design(blueprint, "pips", "standard")
