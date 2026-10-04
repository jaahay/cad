#!/usr/bin/env python3
"""Friendly configurator/exporter for the Tactile Dice project."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from export_project import export_parts, repo_root
from project_registry import discover_projects, load_project_module


PROJECT_SLUG = "tactile-dice"
BACK = "__back__"


def load_dice_project():
    projects = discover_projects()
    try:
        spec = projects[PROJECT_SLUG]
    except KeyError as exc:
        raise SystemExit(f"CAD project {PROJECT_SLUG!r} was not discovered") from exc
    return spec, load_project_module(spec)


def print_options(module) -> None:
    print("Tactile Dice")
    print()
    print("Shapes:")
    for slug, label, description in module.body_options():
        print(f"  {label:<16} {description}  [id: {slug}]")
    print()
    print("Number styles:")
    for slug, label, description in module.mark_options():
        print(f"  {label:<16} {description}  [id: {slug}]")
    print()
    print("For scripted use:")
    print("  ./dice --body mochi-soft --numbers bubbles")
    print("  ./dice --all")


def choose(
    title: str,
    options: tuple[tuple[str, str, str], ...],
    *,
    allow_back: bool,
) -> str | None:
    print()
    print(f"{title}:")
    for index, (_, label, description) in enumerate(options, start=1):
        print(f"  {index}) {label:<16} {description}")

    commands = "B to go back, Q to quit" if allow_back else "Q to quit"
    while True:
        raw = input(f"Choose 1-{len(options)} ({commands}): ").strip().lower()
        if raw in {"q", "quit"}:
            return None
        if allow_back and raw in {"b", "back"}:
            return BACK
        if raw.isdigit():
            index = int(raw)
            if 1 <= index <= len(options):
                return options[index - 1][0]
        print("That choice was not recognized.")


def confirm(body_label: str, number_label: str) -> str:
    print()
    print("Your die:")
    print(f"  Shape:   {body_label}")
    print(f"  Numbers: {number_label}")
    print("  Size:    24 mm")
    print()

    while True:
        raw = input("Create it? [Y] Create  [B] Back  [Q] Quit: ").strip().lower()
        if raw in {"", "y", "yes"}:
            return "create"
        if raw in {"b", "back"}:
            return "back"
        if raw in {"q", "quit"}:
            return "quit"
        print("Enter Y, B, or Q.")


def option_by_slug(
    options: tuple[tuple[str, str, str], ...],
    slug: str,
) -> tuple[str, str, str]:
    for option in options:
        if option[0] == slug:
            return option
    raise ValueError(slug)


def output_directory(body: str, number_style: str) -> Path:
    return (
        repo_root()
        / "build"
        / PROJECT_SLUG
        / "designs"
        / f"{body}--{number_style}"
    )


def export_design(
    module,
    body: str,
    number_style: str,
    *,
    announce: bool = True,
) -> Path:
    parts = module.build_design(body, number_style)
    output = output_directory(body, number_style)
    export_parts(parts, output)

    if announce:
        body_label = option_by_slug(tuple(module.body_options()), body)[1]
        number_label = option_by_slug(tuple(module.mark_options()), number_style)[1]
        print()
        print(f"Created: {body_label} + {number_label}")
        print()
        print("Open this file in Bambu Studio:")
        print(f"  {(output / 'stl' / 'die.stl').relative_to(repo_root())}")
        print()
        print("Editable CAD:")
        print(f"  {(output / 'step' / 'die.step').relative_to(repo_root())}")

    return output


def run_interactive(module) -> int:
    bodies = tuple(module.body_options())
    number_styles = tuple(module.mark_options())

    print("Tactile Dice")
    print("Choose a shape and number style. You can go back before creating.")

    while True:
        body = choose("Choose a shape", bodies, allow_back=False)
        if body is None:
            print("No die created.")
            return 0

        while True:
            number_style = choose(
                "Choose the number style",
                number_styles,
                allow_back=True,
            )
            if number_style is None:
                print("No die created.")
                return 0
            if number_style == BACK:
                break

            body_label = option_by_slug(bodies, body)[1]
            number_label = option_by_slug(number_styles, number_style)[1]
            action = confirm(body_label, number_label)

            if action == "quit":
                print("No die created.")
                return 0
            if action == "back":
                continue

            export_design(module, body, number_style)
            return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a tactile d6 and export STEP/STL files."
    )
    parser.add_argument("--body", help="Shape id to use")
    parser.add_argument("--numbers", help="Number-style id to use")
    parser.add_argument("--list", action="store_true", help="Show available choices")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export every shape/number-style combination",
    )
    args = parser.parse_args(argv)

    _, module = load_dice_project()
    bodies = tuple(module.body_options())
    number_styles = tuple(module.mark_options())
    body_names = {slug for slug, _, _ in bodies}
    number_names = {slug for slug, _, _ in number_styles}

    if args.list:
        if args.body or args.numbers or args.all:
            parser.error("--list cannot be combined with --body, --numbers, or --all")
        print_options(module)
        return 0

    if args.body and args.body not in body_names:
        parser.error(
            f"unknown shape {args.body!r}; choose from: "
            f"{', '.join(slug for slug, _, _ in bodies)}"
        )
    if args.numbers and args.numbers not in number_names:
        parser.error(
            f"unknown number style {args.numbers!r}; choose from: "
            f"{', '.join(slug for slug, _, _ in number_styles)}"
        )

    if args.all:
        if args.body or args.numbers:
            parser.error("--all cannot be combined with --body or --numbers")
        count = 0
        for body, _, _ in bodies:
            for number_style, _, _ in number_styles:
                export_design(module, body, number_style, announce=False)
                count += 1
        print(f"Created {count} Tactile Dice designs under build/tactile-dice/designs.")
        return 0

    if not args.body and not args.numbers:
        return run_interactive(module)

    interactive = sys.stdin.isatty()
    if not args.body:
        if not interactive:
            parser.error("--body is required in non-interactive mode")
        body = choose("Choose a shape", bodies, allow_back=False)
        if body is None:
            print("No die created.")
            return 0
    else:
        body = args.body

    if not args.numbers:
        if not interactive:
            parser.error("--numbers is required in non-interactive mode")
        number_style = choose(
            "Choose the number style",
            number_styles,
            allow_back=False,
        )
        if number_style is None:
            print("No die created.")
            return 0
    else:
        number_style = args.numbers

    export_design(module, body, number_style)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
