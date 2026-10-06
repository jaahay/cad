from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / "tools" / "tactile_dice.py"


def run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_lists_friendly_choices_and_script_ids() -> None:
    result = run_cli("--list")

    assert result.returncode == 0, result.stderr
    assert "Tactile Dice" in result.stdout
    assert "Shapes:" in result.stdout
    assert "Mochi" in result.stdout
    assert "[id: mochi-soft]" in result.stdout
    assert "Number styles:" in result.stdout
    assert "Paws" in result.stdout
    assert "Tactile intensity:" in result.stdout
    assert "Gentle" in result.stdout
    assert "[id: bold]" in result.stdout
    assert "--handoff" in result.stdout
    assert "--batch intensity" in result.stdout
    assert "--batch surprise" in result.stdout


def test_interactive_cli_can_quit_from_workflow_menu() -> None:
    result = run_cli(input_text="q\n")

    assert result.returncode == 0, result.stderr
    assert "What would you like to make?" in result.stdout
    assert "Make one die" in result.stdout
    assert "Prototype batch" in result.stdout
    assert "No files created." in result.stdout


def test_single_die_flow_can_back_out_to_workflow_menu() -> None:
    result = run_cli(input_text="1\n1\n1\nb\nb\nb\nq\n")

    assert result.returncode == 0, result.stderr
    assert result.stdout.count("\nChoose a shape:\n") == 2
    assert "Choose the number style" in result.stdout
    assert "Choose the tactile intensity" in result.stdout
    assert result.stdout.count("\nWhat would you like to make?:\n") == 2
    assert "No files created." in result.stdout


def test_batch_flow_can_back_out_to_workflow_menu() -> None:
    result = run_cli(input_text="2\nb\nq\n")

    assert result.returncode == 0, result.stderr
    assert "Choose the baseline shape" in result.stdout
    assert result.stdout.count("\nWhat would you like to make?:\n") == 2
    assert "No files created." in result.stdout


def test_cli_help_uses_trait_language_and_output_modes() -> None:
    result = run_cli("--help")

    assert result.returncode == 0
    assert "--numbers" in result.stdout
    assert "--marks" not in result.stdout
    assert "--intensity" in result.stdout
    assert "--handoff" in result.stdout
    assert "--batch {shape,numbers,intensity,surprise}" in result.stdout
    assert "one trait" in result.stdout
    assert "one axis" not in result.stdout
