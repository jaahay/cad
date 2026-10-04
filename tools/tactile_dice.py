#!/usr/bin/env python3
"""Friendly configurator/exporter for the Tactile Dice project."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from export_project import export_parts, repo_root
from project_registry import discover_projects, load_project_module


PROJECT_SLUG = "tactile-dice"


def load_dice_project():
    projects = discover_projects()
    try:
        spec = projects[PROJECT_SLUG]
    except KeyError as exc:
        raise SystemExit(f"CAD project {PROJECT_SLUG!r} was not discovered") from exc
    return spec, load_project_module(spec)


def print_options(module) -> None:
    print("Tactile Dice Designer")
    print()
    print("Bodies:")
    for slug, description in module.body_options():
        print(f"  {slug:<16} {description}")
    print()
    print("Mark styles:")
    for slug, description in module.mark_options():
        print(f"  {slug:<16} {description}")
    print()
    print("Examples:")
    print("  uv run python tools/tactile_dice.py")
    print(
        "  uv run python tools/tactile_dice.py "
        "--body mochi-soft --marks bubbles"
    )
    print("  uv run python tools/tactile_dice.py --all")


def choose(title: str, options: tuple[tuple[str, str], ...]) -> str:
    print()
    print(f"{title}:")
    for index, (slug, description) in enumerate(options, start=1):
        print(f"  {index}) {slug:<16} {description}")

    while True:
        raw = input(f"Choose 1-{len(options)} [1]: ").strip()
        if not raw:
            return options[0][0]
        if raw.isdigit():
            index = int(raw)
            if 1 <= index <= len(options):
                return options[index - 1][0]
        print(f"Enter a number from 1 to {len(options)}.")


def output_directory(body: str, marks: str) -> Path:
    return repo_root() / "build" / PROJECT_SLUG / "designs" / f"{body}--{marks}"


def export_design(module, body: str, marks: str) -> Path:
    parts = module.build_design(body, marks)
    output = output_directory(body, marks)
    export_parts(parts, output)
    print(
        f"Exported {body} + {marks} to "
        f"{output.relative_to(repo_root())}"
    )
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Choose a Tactile Dice body and tactile mark style, then export STEP/STL."
        )
    )
    parser.add_argument("--body", help="Body design to use")
    parser.add_argument("--marks", help="Tactile count-mark style to use")
    parser.add_argument("--list", action="store_true", help="Show available choices")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export every body/mark combination",
    )
    args = parser.parse_args(argv)

    _, module = load_dice_project()
    bodies = tuple(module.body_options())
    marks = tuple(module.mark_options())
    body_names = {name for name, _ in bodies}
    mark_names = {name for name, _ in marks}

    if args.list:
        if args.body or args.marks or args.all:
            parser.error("--list cannot be combined with --body, --marks, or --all")
        print_options(module)
        return 0

    if args.body and args.body not in body_names:
        parser.error(
            f"unknown body {args.body!r}; choose from: {', '.join(name for name, _ in bodies)}"
        )
    if args.marks and args.marks not in mark_names:
        parser.error(
            f"unknown mark style {args.marks!r}; "
            f"choose from: {', '.join(name for name, _ in marks)}"
        )

    if args.all:
        if args.body or args.marks:
            parser.error("--all cannot be combined with --body or --marks")
        count = 0
        for body, _ in bodies:
            for mark_style, _ in marks:
                export_design(module, body, mark_style)
                count += 1
        print(f"Exported {count} Tactile Dice designs.")
        return 0

    interactive = sys.stdin.isatty()
    if not args.body and not interactive:
        parser.error("body is required in non-interactive mode; use --list to see choices")
    if not args.marks and not interactive:
        parser.error("marks are required in non-interactive mode; use --list to see choices")

    body = args.body or choose("Body", bodies)
    mark_style = args.marks or choose("Mark style", marks)

    print()
    print(f"Design: {body} + {mark_style}")
    export_design(module, body, mark_style)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
