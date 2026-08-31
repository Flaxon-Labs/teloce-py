import shutil
import time
from pathlib import Path

import pytest

from teloce.build import build_project
from teloce.cli.server import start_dev_server
from tests.integration.test_browser_e2e import _chrome, _dump_dom


ROOT = Path(__file__).parents[2]


@pytest.mark.skipif(_chrome() is None, reason="Chrome is not installed")
def test_live_gallery_mounts_compiled_vel_components(tmp_path: Path):
    project = tmp_path / "gallery"
    shutil.copytree(
        ROOT / "examples" / "teloce-gallery",
        project,
        ignore=shutil.ignore_patterns("dist", "__pycache__", "*.pyc"),
    )
    build_project(project, options={"dev": True, "clean": True, "source_maps": False})
    server = start_dev_server("127.0.0.1", 0, project / "dist")
    try:
        time.sleep(0.1)
        result = _dump_dom(f"http://127.0.0.1:{server.server_port}/?no_hmr=1", 2000)
        assert result.returncode == 0, result.stderr
        assert "Collect the useful web." in result.stdout
        assert "Gallery could not start" not in result.stdout
        assert "Loading gallery" not in result.stdout
    finally:
        server.shutdown()
        server.server_close()
