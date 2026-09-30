"""Repository-facing contract for the Weekly Pill Organizer project."""

from __future__ import annotations

from importlib import import_module

import cadquery as cq


BLUEPRINT_MODULES = {
    "rotary-vault": "weekly_pill_organizer.blueprints.rotary_vault",
}


def blueprints() -> tuple[str, ...]:
    return tuple(BLUEPRINT_MODULES)


def validate_project() -> None:
    if not BLUEPRINT_MODULES:
        raise ValueError("Weekly Pill Organizer must expose at least one blueprint")


def build(blueprint: str) -> dict[str, cq.Shape]:
    validate_project()
    try:
        module_name = BLUEPRINT_MODULES[blueprint]
    except KeyError as exc:
        raise ValueError(
            f"Unknown weekly-pill-organizer blueprint: {blueprint}"
        ) from exc

    module = import_module(module_name)
    module.validate_blueprint()
    return module.build()
