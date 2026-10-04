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
    assert "Recessed pips" in result.stdout
    assert "[id: bubbles]" in result.stdout


def test_interactive_cli_can_quit_without_creating_a_die() -> None:
    result = run_cli(input_text="q\n")

    assert result.returncode == 0, result.stderr
    assert "Choose a shape" in result.stdout
    assert "No die created." in result.stdout


def test_interactive_cli_can_go_back_from_number_style() -> None:
    result = run_cli(input_text="1\nb\nq\n")

    assert result.returncode == 0, result.stderr
    assert result.stdout.count("\nChoose a shape:\n") == 2
    assert "Choose the number style" in result.stdout
    assert "No die created." in result.stdout


def test_cli_help_uses_user_facing_number_language() -> None:
    result = run_cli("--help")

    assert result.returncode == 0
    assert "--numbers" in result.stdout
    assert "--marks" not in result.stdout
