from pathlib import Path
import subprocess
import sys


def test_cli_lists_body_and_mark_choices() -> None:
    root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, str(root / "tools" / "tactile_dice.py"), "--list"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Tactile Dice Designer" in result.stdout
    assert "nested-steps" in result.stdout
    assert "bubbles" in result.stdout
    assert "buttons" in result.stdout
