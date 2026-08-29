from pathlib import Path

import pytest

from teloce.build.esbuild import EsbuildBundler, EsbuildUnavailable


def test_esbuild_backend_reports_an_actionable_missing_tool_error(tmp_path: Path):
    bundler = EsbuildBundler(tmp_path, executable=None)
    bundler.executable = None
    with pytest.raises(EsbuildUnavailable, match="npm install --save-dev esbuild"):
        bundler.bundle(tmp_path / "App.js")
