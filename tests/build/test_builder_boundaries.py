"""Regression tests for safe project build boundaries."""

from pathlib import Path

from teloce.build.builder import Builder


def _component(path: Path, name: str = "App") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"<template><main>{name}</main></template>\n"
        f"<script>export default {{ name: '{name}' }};</script>\n",
        encoding="utf-8",
    )


def test_build_does_not_scan_or_copy_output_into_itself(tmp_path):
    root = tmp_path / "project"
    output = root / "public"
    _component(root / "static" / "js" / "App.vel")
    # This is generated-looking content and must not become a second source.
    _component(output / "static" / "js" / "Old.vel", "Old")
    (output / "app.js").write_text("console.log('asset');", encoding="utf-8")

    result = Builder({"clean": False, "source_maps": False}).build(root, output)

    assert result["total"] == 1
    assert result["failed"] == 0
    assert (output / "static" / "js" / "App.js").is_file()
    assert not (output / "public" / "static" / "js" / "App.js").exists()

