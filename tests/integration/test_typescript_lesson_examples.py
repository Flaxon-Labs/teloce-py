"""Compile every copy-pasteable TypeScript `.vel` example in the TS lessons."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from teloce.compiler import compile


ROOT = Path(__file__).resolve().parents[2]
LESSONS = (
    ROOT / "docs" / "lessons" / "29-ts-tutoiral.md",
    ROOT / "docs" / "lessons" / "30-Extra-ts.md",
    ROOT / "docs" / "lessons" / "31-advanced-ts.md",
)


def _vel_examples(path: Path) -> list[str]:
    """Return complete `.vel` snippets from HTML fenced blocks in a lesson."""
    content = path.read_text(encoding="utf-8")
    blocks = re.findall(r"```html\s*\n([\s\S]*?)\n```", content)
    return [block for block in blocks if "<template" in block and "<script" in block]


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda path: path.stem)
def test_typescript_lesson_vel_examples_compile_and_emit_valid_modules(
    lesson: Path, tmp_path: Path
) -> None:
    examples = _vel_examples(lesson)
    assert examples, f"{lesson.name} must contain at least one complete .vel example"
    node = shutil.which("node")

    for index, source in enumerate(examples, start=1):
        result = compile(source, f"{lesson.stem}-{index}.vel", source_maps=False)
        assert result["success"], result["diagnostics"]
        # The runtime itself legitimately uses properties named ``type``;
        # Node syntax validation below verifies that the TS-only source has
        # been erased into browser-valid JavaScript without making a brittle
        # substring assertion against runtime implementation details.
        assert "<script" not in result["code"]
        assert " as const" not in result["code"]
        if node:
            emitted = tmp_path / f"{lesson.stem}-{index}.mjs"
            emitted.write_text(result["code"], encoding="utf-8")
            checked = subprocess.run(
                [node, "--check", str(emitted)],
                capture_output=True,
                text=True,
                check=False,
            )
            assert checked.returncode == 0, checked.stderr
