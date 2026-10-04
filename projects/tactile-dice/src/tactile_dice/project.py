"""Repository-facing contract for the Tactile Dice project."""

from __future__ import annotations

from importlib import import_module

import cadquery as cq

from .common.die import MARK_STYLES, finish_die, validate_definition


BODY_DESCRIPTIONS = {
    "mochi-soft": "Soft rounded baseline.",
    "spherocube": "Heavily rounded, almost ball-like cube.",
    "facet": "Broad chamfers and crisp planar facets.",
    "edge-channel": "Shallow perimeter channels around the body.",
    "corner-pocket": "Symmetric scallops carved into all eight corners.",
    "nested-steps": "Two shallow inset face levels form a tactile frame.",
}

MARK_DESCRIPTIONS = {
    "pips": "Classic shallow recessed round pips.",
    "bubbles": "Low rounded bumps; one bump is one count.",
    "buttons": "Broad low flat-topped bumps; one button is one count.",
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


def body_options() -> tuple[tuple[str, str], ...]:
    return tuple(BODY_DESCRIPTIONS.items())


def mark_options() -> tuple[tuple[str, str], ...]:
    return tuple(MARK_DESCRIPTIONS.items())


def validate_project() -> None:
    validate_definition()
    if tuple(MARK_DESCRIPTIONS) != MARK_STYLES:
        raise ValueError("Tactile Dice mark descriptions must match supported mark styles")
    if tuple(BODY_DESCRIPTIONS) != blueprints():
        raise ValueError("Tactile Dice body descriptions must match blueprints")


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


def build_design(body_name: str, mark_style: str) -> dict[str, cq.Shape]:
    validate_project()
    if mark_style not in MARK_DESCRIPTIONS:
        raise ValueError(f"Unknown tactile-dice mark style: {mark_style}")
    return {"die": finish_die(build_body(body_name), mark_style)}


def build(blueprint: str) -> dict[str, cq.Shape]:
    """Repository blueprint builds use classic recessed pips."""
    return build_design(blueprint, "pips")
