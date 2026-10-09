#!/usr/bin/env python3
"""Friendly configurator/exporter for the Tactile Dice project."""

from __future__ import annotations

import argparse
from importlib import import_module
from pathlib import Path
import shutil
import sys

from cadquery import exporters

from export_project import export_parts, normalize_stl, repo_root
from project_registry import discover_projects, load_project_module


PROJECT_SLUG = "tactile-dice"
BACK = "__back__"

WORKFLOW_OPTIONS = (
    ("single", "Make one die", "Create a neutral print handoff."),
    ("batch", "Prototype batch", "Compare one controlled change on one plate."),
)

BATCH_TRAIT_OPTIONS = (
    ("shape", "Shape", "Keep the other traits fixed and compare shapes."),
    ("numbers", "Number style", "Keep the other traits fixed and compare number styles."),
    ("intensity", "Tactile intensity", "Compare Gentle, Standard, and Bold."),
    ("surprise", "Surprise one trait", "Pick one trait for us to explore."),
)


def load_dice_project():
    projects = discover_projects()
    try:
        spec = projects[PROJECT_SLUG]
    except KeyError as exc:
        raise SystemExit(f"CAD project {PROJECT_SLUG!r} was not discovered") from exc
    return spec, load_project_module(spec)


def handoff_api():
    """Load project-specific handoff helpers after project discovery sets sys.path."""
    return import_module("tactile_dice.handoff")


def manufacturing_api():
    """Load project-specific manufacturing helpers after project discovery."""
    return import_module("tactile_dice.manufacturing")


def export_showcase_stl(die, destination: Path) -> Path:
    """Export the derived edge-down manufacturing model as one normalized STL."""
    model = manufacturing_api().build_showcase_print(die)
    print_dir = destination / "print"
    print_dir.mkdir(parents=True, exist_ok=True)
    path = print_dir / "showcase.stl"
    exporters.export(
        model,
        str(path),
        tolerance=0.03,
        angularTolerance=0.08,
    )
    normalize_stl(path)
    return path


def print_options(module) -> None:
    print("Tactile Dice")
    print()
    print("Shapes:")
    for slug, label, description in module.body_options():
        print(f"  {label:<18} {description}  [id: {slug}]")
    print()
    print("Number styles:")
    for slug, label, description in module.mark_options():
        print(f"  {label:<18} {description}  [id: {slug}]")
    print()
    print("Tactile intensity:")
    for slug, label, description in module.intensity_options():
        print(f"  {label:<18} {description}  [id: {slug}]")
    print()
    print("For scripted use:")
    print("  ./dice --body mochi-soft --numbers paws --intensity bold")
    print("  ./dice --body mochi-soft --numbers paws --intensity bold --handoff")
    print("  ./dice --body mochi-soft --numbers paws --batch intensity")
    print("  ./dice --body mochi-soft --numbers paws --batch surprise")
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
        print(f"  {index}) {label:<20} {description}")

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


def confirm_design(
    body_label: str,
    number_label: str,
    intensity_label: str,
    prompt: str,
) -> str:
    print()
    print("Your die:")
    print(f"  Shape:     {body_label}")
    print(f"  Numbers:   {number_label}")
    print(f"  Intensity: {intensity_label}")
    print("  Size:      24 mm")
    print()

    while True:
        raw = input(f"{prompt} [Y] Yes  [B] Back  [Q] Quit: ").strip().lower()
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


def design_ref(module, body: str, number_style: str, intensity: str):
    api = handoff_api()
    body_label = option_by_slug(tuple(module.body_options()), body)[1]
    number_label = option_by_slug(tuple(module.mark_options()), number_style)[1]
    intensity_label = option_by_slug(tuple(module.intensity_options()), intensity)[1]
    return api.DesignRef(
        spec=module.DesignSpec(body, number_style, intensity),
        shape_label=body_label,
        number_label=number_label,
        intensity_label=intensity_label,
    )


def output_directory(body: str, number_style: str, intensity: str) -> Path:
    return (
        repo_root()
        / "build"
        / PROJECT_SLUG
        / "designs"
        / f"{body}--{number_style}--{intensity}"
    )


def handoff_directory(body: str, number_style: str, intensity: str) -> Path:
    return (
        repo_root()
        / "build"
        / PROJECT_SLUG
        / "handoffs"
        / f"{body}--{number_style}--{intensity}"
    )


def batch_directory(
    body: str,
    number_style: str,
    intensity: str,
    trait: str,
) -> Path:
    return (
        repo_root()
        / "build"
        / PROJECT_SLUG
        / "prototype-batches"
        / f"{body}--{number_style}--{intensity}--vary-{trait}"
    )


def export_design(
    module,
    body: str,
    number_style: str,
    intensity: str = "standard",
    *,
    announce: bool = True,
) -> Path:
    parts = module.build_design(body, number_style, intensity)
    output = output_directory(body, number_style, intensity)
    export_parts(parts, output)

    if announce:
        design = design_ref(module, body, number_style, intensity)
        print()
        print(
            f"Created: {design.shape_label} + {design.number_label} + "
            f"{design.intensity_label}"
        )
        print()
        print("STL:")
        print(f"  {(output / 'stl' / 'die.stl').relative_to(repo_root())}")
        print()
        print("Editable CAD:")
        print(f"  {(output / 'step' / 'die.step').relative_to(repo_root())}")

    return output


def create_handoff(
    module,
    body: str,
    number_style: str,
    intensity: str = "standard",
    *,
    output: Path | None = None,
    announce: bool = True,
) -> Path:
    api = handoff_api()
    design = design_ref(module, body, number_style, intensity)
    destination = output or handoff_directory(body, number_style, intensity)

    parts = module.build_design(body, number_style, intensity)
    export_parts(parts, destination)
    showcase_path = export_showcase_stl(parts["die"], destination)
    api.write_handoff_manifest(destination, design)

    if announce:
        print()
        print(
            f"Created print handoff: {design.shape_label} + "
            f"{design.number_label} + {design.intensity_label}"
        )
        print(f"  {destination.relative_to(repo_root())}")
        print()
        print("Recommended print STL (1-2 edge down + breakaway rail):")
        print(f"  {showcase_path.relative_to(repo_root())}")
        print()
        print("Canonical STL:")
        print(f"  {(destination / 'stl' / 'die.stl').relative_to(repo_root())}")
        print()
        print("Editable CAD:")
        print(f"  {(destination / 'step' / 'die.step').relative_to(repo_root())}")
        print()
        print("Handoff manifest:")
        print(f"  {(destination / 'manifest.json').relative_to(repo_root())}")

    return destination


def create_prototype_batch(
    module,
    body: str,
    number_style: str,
    intensity: str,
    requested_trait: str,
    *,
    resolved_trait: str | None = None,
    announce: bool = True,
) -> Path:
    api = handoff_api()
    bodies = tuple(slug for slug, _, _ in module.body_options())
    number_styles = tuple(slug for slug, _, _ in module.mark_options())
    intensities = tuple(slug for slug, _, _ in module.intensity_options())
    baseline = design_ref(module, body, number_style, intensity)
    varied_trait = resolved_trait or api.resolve_trait(requested_trait)
    specs = api.variation_specs(
        baseline.spec,
        varied_trait,
        bodies,
        number_styles,
        intensities,
    )
    output = batch_directory(body, number_style, intensity, varied_trait)

    if output.exists():
        shutil.rmtree(output)

    candidates = []
    for index, candidate_spec in enumerate(specs):
        label = api.candidate_label(index)
        design = design_ref(
            module,
            candidate_spec.body,
            candidate_spec.number_style,
            candidate_spec.intensity,
        )
        candidate_name = f"{label}-{design.slug}"
        candidate_dir = output / "candidates" / candidate_name

        create_handoff(
            module,
            candidate_spec.body,
            candidate_spec.number_style,
            candidate_spec.intensity,
            output=candidate_dir,
            announce=False,
        )
        plate_stl = api.copy_plate_stl(
            candidate_dir / "print" / "showcase.stl",
            output / "plate",
            label,
            design,
        )
        candidates.append(
            api.BatchCandidate(
                label=label,
                design=design,
                handoff_dir=f"candidates/{candidate_name}",
                plate_stl=f"plate/{plate_stl.name}",
            )
        )

    api.write_batch_summary(
        output,
        baseline,
        requested_trait,
        varied_trait,
        tuple(candidates),
    )

    if announce:
        print()
        print(
            f"Created prototype batch: {len(candidates)} candidates, "
            f"varying {api.TRAIT_LABELS[varied_trait].lower()}."
        )
        if requested_trait == "surprise":
            print(f"Surprise chose: {api.TRAIT_LABELS[varied_trait]}")
        print(f"  {output.relative_to(repo_root())}")
        print()
        print("Drop all STL files from this folder into Bambu Studio:")
        print(f"  {(output / 'plate').relative_to(repo_root())}")
        print()
        for candidate in candidates:
            print(
                f"  {candidate.label}) "
                f"{candidate.design.shape_label} + "
                f"{candidate.design.number_label} + "
                f"{candidate.design.intensity_label}"
            )

    return output


def run_single_interactive(module) -> str:
    bodies = tuple(module.body_options())
    number_styles = tuple(module.mark_options())
    intensities = tuple(module.intensity_options())

    while True:
        body = choose("Choose a shape", bodies, allow_back=True)
        if body is None:
            return "quit"
        if body == BACK:
            return "back"

        while True:
            number_style = choose(
                "Choose the number style",
                number_styles,
                allow_back=True,
            )
            if number_style is None:
                return "quit"
            if number_style == BACK:
                break

            while True:
                intensity = choose(
                    "Choose the tactile intensity",
                    intensities,
                    allow_back=True,
                )
                if intensity is None:
                    return "quit"
                if intensity == BACK:
                    break

                body_label = option_by_slug(bodies, body)[1]
                number_label = option_by_slug(number_styles, number_style)[1]
                intensity_label = option_by_slug(intensities, intensity)[1]
                action = confirm_design(
                    body_label,
                    number_label,
                    intensity_label,
                    "Create print handoff?",
                )
                if action == "quit":
                    return "quit"
                if action == "back":
                    continue

                create_handoff(module, body, number_style, intensity)
                return "created"


def run_batch_interactive(module) -> str:
    bodies = tuple(module.body_options())
    number_styles = tuple(module.mark_options())
    intensities = tuple(module.intensity_options())

    while True:
        body = choose("Choose the baseline shape", bodies, allow_back=True)
        if body is None:
            return "quit"
        if body == BACK:
            return "back"

        while True:
            number_style = choose(
                "Choose the baseline number style",
                number_styles,
                allow_back=True,
            )
            if number_style is None:
                return "quit"
            if number_style == BACK:
                break

            while True:
                intensity = choose(
                    "Choose the baseline tactile intensity",
                    intensities,
                    allow_back=True,
                )
                if intensity is None:
                    return "quit"
                if intensity == BACK:
                    break

                while True:
                    requested_trait = choose(
                        "What should change?",
                        BATCH_TRAIT_OPTIONS,
                        allow_back=True,
                    )
                    if requested_trait is None:
                        return "quit"
                    if requested_trait == BACK:
                        break

                    api = handoff_api()
                    varied_trait = api.resolve_trait(requested_trait)
                    baseline = design_ref(module, body, number_style, intensity)
                    specs = api.variation_specs(
                        baseline.spec,
                        varied_trait,
                        tuple(slug for slug, _, _ in bodies),
                        tuple(slug for slug, _, _ in number_styles),
                        tuple(slug for slug, _, _ in intensities),
                    )

                    print()
                    print("Prototype batch:")
                    print(
                        f"  Baseline: {baseline.shape_label} + "
                        f"{baseline.number_label} + {baseline.intensity_label}"
                    )
                    if requested_trait == "surprise":
                        print(f"  Surprise: {api.TRAIT_LABELS[varied_trait]}")
                    else:
                        print(f"  Change:   {api.TRAIT_LABELS[varied_trait]}")
                    print(f"  Pieces:   {len(specs)}")

                    action = confirm_design(
                        baseline.shape_label,
                        baseline.number_label,
                        baseline.intensity_label,
                        "Create prototype batch?",
                    )
                    if action == "quit":
                        return "quit"
                    if action == "back":
                        continue

                    create_prototype_batch(
                        module,
                        body,
                        number_style,
                        intensity,
                        requested_trait,
                        resolved_trait=varied_trait,
                    )
                    return "created"


def run_interactive(module) -> int:
    print("Tactile Dice")
    print("Make one die or compare a controlled set of variants.")

    while True:
        workflow = choose(
            "What would you like to make?",
            WORKFLOW_OPTIONS,
            allow_back=False,
        )
        if workflow is None:
            print("No files created.")
            return 0

        if workflow == "single":
            result = run_single_interactive(module)
        elif workflow == "batch":
            result = run_batch_interactive(module)
        else:
            raise AssertionError(workflow)

        if result == "quit":
            print("No files created.")
            return 0
        if result == "created":
            return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create tactile d6 designs, print handoffs, and prototype batches."
    )
    parser.add_argument("--body", help="Shape id to use")
    parser.add_argument("--numbers", help="Number-style id to use")
    parser.add_argument("--intensity", help="Tactile-intensity id to use")
    parser.add_argument("--list", action="store_true", help="Show available choices")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export every shape/number-style/intensity combination",
    )
    parser.add_argument(
        "--handoff",
        action="store_true",
        help="Create a neutral single-design print handoff",
    )
    parser.add_argument(
        "--batch",
        choices=("shape", "numbers", "intensity", "surprise"),
        help="Create a baseline-first prototype batch changing one trait",
    )
    args = parser.parse_args(argv)

    _, module = load_dice_project()
    bodies = tuple(module.body_options())
    number_styles = tuple(module.mark_options())
    intensities = tuple(module.intensity_options())
    body_names = {slug for slug, _, _ in bodies}
    number_names = {slug for slug, _, _ in number_styles}
    intensity_names = {slug for slug, _, _ in intensities}

    if args.list:
        if (
            args.body
            or args.numbers
            or args.intensity
            or args.all
            or args.handoff
            or args.batch
        ):
            parser.error(
                "--list cannot be combined with --body, --numbers, --intensity, "
                "--all, --handoff, or --batch"
            )
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
    if args.intensity and args.intensity not in intensity_names:
        parser.error(
            f"unknown tactile intensity {args.intensity!r}; choose from: "
            f"{', '.join(slug for slug, _, _ in intensities)}"
        )

    if args.all:
        if args.body or args.numbers or args.intensity or args.handoff or args.batch:
            parser.error(
                "--all cannot be combined with --body, --numbers, --intensity, "
                "--handoff, or --batch"
            )
        count = 0
        for body, _, _ in bodies:
            for number_style, _, _ in number_styles:
                for intensity, _, _ in intensities:
                    export_design(
                        module,
                        body,
                        number_style,
                        intensity,
                        announce=False,
                    )
                    count += 1
        print(
            f"Created {count} Tactile Dice designs under "
            "build/tactile-dice/designs."
        )
        return 0

    if args.handoff and args.batch:
        parser.error("--handoff and --batch are separate output modes")

    if (
        not args.body
        and not args.numbers
        and not args.intensity
        and not args.handoff
        and not args.batch
    ):
        return run_interactive(module)

    interactive = sys.stdin.isatty()
    if not args.body:
        if not interactive:
            parser.error("--body is required in non-interactive mode")
        body = choose("Choose a shape", bodies, allow_back=False)
        if body is None:
            print("No files created.")
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
            print("No files created.")
            return 0
    else:
        number_style = args.numbers

    intensity = args.intensity or "standard"

    if args.batch:
        create_prototype_batch(
            module,
            body,
            number_style,
            intensity,
            args.batch,
        )
    elif args.handoff:
        create_handoff(module, body, number_style, intensity)
    else:
        export_design(module, body, number_style, intensity)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
