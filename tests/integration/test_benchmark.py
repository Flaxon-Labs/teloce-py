from pathlib import Path

import pytest

from teloce.cli.benchmark import benchmark_project


def test_benchmark_compiles_project_components(tmp_path: Path):
    (tmp_path / "App.vel").write_text(
        "<template><h1>{{ title }}</h1></template>\n"
        "<script>export default { data() { return { title: 'Hello' }; } }</script>",
        encoding="utf-8",
    )

    result = benchmark_project(tmp_path, iterations=2)

    assert result["files"] == 1
    assert result["iterations"] == 2
    assert result["compiled"] == 2
    assert result["failed"] == 0
    assert result["seconds"] >= 0
    assert result["peak_memory_bytes"] >= 0


def test_benchmark_rejects_non_positive_iterations(tmp_path: Path):
    with pytest.raises(ValueError, match="at least 1"):
        benchmark_project(tmp_path, iterations=0)
