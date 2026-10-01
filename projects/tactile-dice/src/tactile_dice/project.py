"""Repository-facing contract for the Tactile Dice project."""

from __future__ import annotations

from importlib import import_module

import cadquery as cq

from .common.die import validate_definition


BLUEPRINT_MODULES = {
    "mochi-soft": "tactile_dice.blueprints.mochi",
    "spherocube": "tactile_dice.blueprints.spherocube",
    "facet": "tactile_dice.blueprints.facet",
    "edge-channel": "tactile_dice.blueprints.edge_channel",
    "corner-pocket": "tactile_dice.blueprints.corner_pocket",
}


def blueprints() -> tuple[str, ...]:
    return tuple(BLUEPRINT_MODULES)


def validate_project() -> None:
    validate_definition()


def build(blueprint: str) -> dict[str, cq.Shape]:
    validate_project()
    try:
        module_name = BLUEPRINT_MODULES[blueprint]
    except KeyError as exc:
        raise ValueError(f"Unknown tactile-dice blueprint: {blueprint}") from exc

    module = import_module(module_name)
    parts = module.build()
    if set(parts) != {"die"}:
        raise ValueError(f"{blueprint}: tactile die blueprints must export one 'die' part")
    return parts
